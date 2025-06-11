import json
import numpy as np
from sentence_transformers import SentenceTransformer, util
from sklearn.feature_extraction.text import CountVectorizer

# Correct model load for Render
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def classify_intent(question):
    q = question.lower()
    if q.startswith("what"):
        return "what"
    elif q.startswith("why"):
        return "why"
    elif q.startswith("how"):
        return "how"
    return "other"

def semantic_search(question, chunks, top_k=10):
    question_embedding = model.encode(question, convert_to_tensor=True)
    scored_chunks = []

    for chunk in chunks:
        content = chunk.get("text", "")
        chunk_embedding = model.encode(content, convert_to_tensor=True)
        score = float(util.pytorch_cos_sim(question_embedding, chunk_embedding)[0])
        scored_chunks.append((chunk, score))

    scored_chunks.sort(key=lambda x: x[1], reverse=True)
    top_matches = scored_chunks[:top_k]

    results = []
    for match, score in top_matches:
        results.append({
            "document": match.get("document_title", ""),
            "section": match.get("section", ""),
            "content": match.get("text", ""),
            "score": round(score, 4),
            "reason": f"Matched semantically with score {round(score, 4)}"
        })

    return results
