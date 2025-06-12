import re
from sentence_transformers import SentenceTransformer, util

# Load model once
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def clean_snippet(text):
    return re.sub(r'\s+', ' ', text.replace('\n', ' ')).strip()

def answer_with_semantic(query, chunks, selected_doc, refine_query):
    query_embedding = model.encode(query, convert_to_tensor=True)

    # Filter chunks by document and refine terms BEFORE encoding
    filtered_chunks = []
    for c in chunks:
        doc = c.get('document', '')
        if selected_doc and doc != selected_doc:
            continue
        content = c.get('content', '')
        if refine_query and refine_query.lower() not in content.lower():
            continue
        filtered_chunks.append(c)

    if not filtered_chunks:
        return []

    # Batch encode content to reduce memory usage
    texts = [c.get('content', '') for c in filtered_chunks]
    chunk_embeddings = model.encode(texts, convert_to_tensor=True)

    # Compute cosine similarity in batch
    scores = util.pytorch_cos_sim(query_embedding, chunk_embeddings)[0]

    matches = []
    for i, score in enumerate(scores):
        if score.item() > 0.45:
            matches.append({
                'document': filtered_chunks[i].get('document', ''),
                'section': filtered_chunks[i].get('section', ''),
                'text': clean_snippet(filtered_chunks[i].get('content', '')),
                'score': round(score.item(), 3),
                'reason': f"Semantic match (score {round(score.item(), 3)})"
            })

    matches.sort(key=lambda x: x['score'], reverse=True)
    return matches

def answer_with_keyword(query, chunks, selected_doc, refine_query):
    q = query.lower()
    matches = []
    for c in chunks:
        doc = c.get('document', '')
        if selected_doc and doc != selected_doc:
            continue
        content = c.get('content', '')
        if refine_query and refine_query.lower() not in content.lower():
            continue
        if q in content.lower():
            matches.append({
                'document': doc,
                'section': c.get('section', ''),
                'text': clean_snippet(content),
                'score': 1.0,
                'reason': "Keyword match"
            })
    return matches

def get_answers(question, chunks, selected_doc, refine_query, use_semantic):
    if use_semantic:
        print("[DEBUG] Running Semantic Matching")
        return answer_with_semantic(question, chunks, selected_doc, refine_query)
    else:
        print("[DEBUG] Running Keyword Matching")
        return answer_with_keyword(question, chunks, selected_doc, refine_query)
