import json
import numpy as np
from sentence_transformers import SentenceTransformer, util
from sklearn.feature_extraction.text import CountVectorizer

# Correct local model load for Render
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def classify_intent(question):
    q = question.lower()
    if q.startswith("how"): return "how"
    if q.startswith("what"): return "what"
    if q.startswith("why"): return "why"
    if q.startswith("when"): return "when"
    return "unknown"

def co_occurrence_score(text, query_terms):
    count = sum(term in text.lower() for term in query_terms)
    return count / len(query_terms) if query_terms else 0

def extract_terms(query):
    return [t.strip() for t in query.lower().split() if len(t.strip()) > 2]

def semantic_search(chunks, query, top_k=10):
    query_embedding = model.encode(query, convert_to_tensor=True)
    chunk_texts = [c["text"] for c in chunks]
    chunk_embeddings = model.encode(chunk_texts, convert_to_tensor=True)

    scores = util.cos_sim(query_embedding, chunk_embeddings)[0]
    query_terms = extract_terms(query)
    intent = classify_intent(query)

    results = []
    for idx, score in enumerate(scores):
        chunk = chunks[idx]
        reason = []

        if score >= 0.25:
            reason.append("semantic match ≥ 0.25")

        co_score = co_occurrence_score(chunk["text"], query_terms)
        if co_score > 0:
            reason.append(f"{int(co_score * 100)}% query term co-occurrence")

        if reason:
            results.append({
                "document": chunk.get("document_title", ""),
                "section": chunk.get("section", ""),
                "content": chunk["text"],
                "score": float(score),
                "reason": "; ".join(reason),
                "intent": intent
            })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]
