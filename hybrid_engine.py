from sentence_transformers import SentenceTransformer, util
import torch
import re

model = SentenceTransformer("all-MiniLM-L6-v2")

def clean(text):
    return re.sub(r"\s+", " ", text.strip())

def keyword_match(question, chunks, selected_doc, refine_query):
    q_words = set(question.lower().split())
    refine_words = set(refine_query.lower().split()) if refine_query else set()
    results = []

    for c in chunks:
        if selected_doc and c.get("document") != selected_doc:
            continue

        fulltext = f"{c.get('content', '')}"
        fulltext_lower = fulltext.lower()

        if all(word in fulltext_lower for word in q_words.union(refine_words)):
            results.append({
                "document": c.get("document"),
                "section": c.get("section", "Uncategorised"),
                "text": clean(fulltext)
            })

    return results

def hybrid_rerank(question, results):
    if not results:
        return []

    question_embedding = model.encode(question, convert_to_tensor=True)
    reranked = []

    for r in results[:20]:  # Only rerank top 20 results
        chunk_embedding = model.encode(r['text'], convert_to_tensor=True)
        score = util.cos_sim(question_embedding, chunk_embedding).item()
        r["score"] = round(score, 4)
        reranked.append(r)

    reranked.sort(key=lambda x: x["score"], reverse=True)
    return reranked

def get_answers(question, chunks, selected_doc, refine_query, semantic_mode):
    selected = selected_doc if selected_doc else ""
    matches = keyword_match(question, chunks, selected, refine_query)
    reranked = hybrid_rerank(question, matches)
    return reranked if reranked else matches
