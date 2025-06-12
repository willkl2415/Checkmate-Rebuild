from sentence_transformers import SentenceTransformer, util
import torch

# Load model once
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_answers(question, chunks, selected_document, refine_query, semantic_mode=False):
    # Apply document and refine filters
    filtered_chunks = [
        c for c in chunks
        if (not selected_document or c['document'] == selected_document) and
           (not refine_query or refine_query.lower() in c['content'].lower())
    ]

    # Score chunks based on keyword match count
    def keyword_score(text, query):
        query_terms = query.lower().split()
        text = text.lower()
        return sum(text.count(term) for term in query_terms)

    scored = [
        {
            "text": c["content"],
            "document": c["document"],
            "section": c.get("section", "Uncategorised"),
            "score": keyword_score(c["content"], question),
        }
        for c in filtered_chunks
    ]

    # Select top N by keyword match
    top_chunks = sorted(scored, key=lambda x: x["score"], reverse=True)[:20]

    # Semantic reranking using transformer
    if top_chunks:
        question_embedding = model.encode(question, convert_to_tensor=True)
        chunk_texts = [c["text"] for c in top_chunks]
        chunk_embeddings = model.encode(chunk_texts, convert_to_tensor=True)
        similarities = util.cos_sim(question_embedding, chunk_embeddings)[0]

        for i, chunk in enumerate(top_chunks):
            chunk["semantic_score"] = float(similarities[i])
        
        top_chunks.sort(key=lambda x: x["semantic_score"], reverse=True)

    return top_chunks
