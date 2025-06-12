from sentence_transformers import CrossEncoder
from difflib import SequenceMatcher
import torch

model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

def simple_keyword_score(query, text):
    query = query.lower()
    text = text.lower()
    return SequenceMatcher(None, query, text).ratio()

def get_hybrid_answers(question, chunks, selected_doc, refine_query):
    filtered_chunks = [c for c in chunks if (selected_doc in ["", c["document"]])]
    
    if refine_query:
        filtered_chunks = [c for c in filtered_chunks if refine_query.lower() in c["content"].lower()]

    top_k = 30  # initial shortlist size
    keyword_scored = sorted(filtered_chunks, key=lambda c: simple_keyword_score(question, c["content"]), reverse=True)
    shortlist = keyword_scored[:top_k]

    pairs = [[question, c["content"]] for c in shortlist]
    scores = model.predict(pairs)

    reranked = sorted(zip(shortlist, scores), key=lambda x: x[1], reverse=True)
    final_results = []

    for chunk, score in reranked[:10]:
        final_results.append({
            "document": chunk["document"],
            "section": chunk.get("section", "Uncategorised"),
            "score": round(float(score), 4),
            "content": chunk["content"]
        })

    return final_results
