# answer_engine.py

import re
from sentence_transformers import SentenceTransformer, util
from semantic_query_optimizer import optimise_semantic_query

# Load model once
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def clean_snippet(text):
    return re.sub(r'\s+', ' ', text.replace('\n', ' ')).strip()

def answer_with_semantic(queries, chunks, selected_doc, refine_query):
    query_embeddings = [model.encode(q, convert_to_tensor=True) for q in queries]
    results = []

    filtered_chunks = []
    for c in chunks:
        doc = c.get('document', '')
        if selected_doc and doc != selected_doc:
            continue
        content = c.get('content', '')
        if refine_query and refine_query.lower() not in content.lower():
            continue
        filtered_chunks.append(c)

    print(f"[DEBUG] Total Chunks After Filter: {len(filtered_chunks)}")

    max_chunks = 250
    if len(filtered_chunks) > max_chunks:
        print(f"[DEBUG] Trimming to first {max_chunks} chunks to avoid timeout")
        filtered_chunks = filtered_chunks[:max_chunks]

    if not filtered_chunks:
        return []

    texts = [c.get('content', '') for c in filtered_chunks]
    chunk_embeddings = model.encode(texts, convert_to_tensor=True)

    for q_idx, q_emb in enumerate(query_embeddings):
        scores = util.pytorch_cos_sim(q_emb, chunk_embeddings)[0]
        for i, score in enumerate(scores):
            score_val = score.item()
            if score_val > 0.45:
                results.append({
                    'document': filtered_chunks[i].get('document', ''),
                    'section': filtered_chunks[i].get('section', ''),
                    'text': clean_snippet(filtered_chunks[i].get('content', '')),
                    'score': round(score_val, 3),
                    'reason': f"Semantic match for variant {q_idx+1} (score {round(score_val, 3)})"
                })

    results.sort(key=lambda x: x['score'], reverse=True)
    return results

def answer_with_keyword(query, chunks, selected_doc, refine_query):
    q = query.lower()
    results = []
    for c in chunks:
        doc = c.get('document', '')
        if selected_doc and doc != selected_doc:
            continue
        content = c.get('content', '')
        if refine_query and refine_query.lower() not in content.lower():
            continue
        if q in content.lower():
            results.append({
                'document': doc,
                'section': c.get('section', ''),
                'text': clean_snippet(content),
                'score': 1.0,
                'reason': "Keyword match"
            })
    return results

def get_answers(question, chunks, selected_doc, refine_query, use_semantic):
    if use_semantic:
        print("[DEBUG] Running Semantic Matching")
        variants = optimise_semantic_query(question)
        print(f"[DEBUG] Semantic Variants: {variants}")
        return answer_with_semantic(variants, chunks, selected_doc, refine_query)
    else:
        print("[DEBUG] Running Keyword Matching")
        return answer_with_keyword(question, chunks, selected_doc, refine_query)
