from sentence_transformers import SentenceTransformer, util
import torch

# Load transformer model once
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_hybrid_answers(question, chunks, selected_document="", refine_query=""):
    # Step 1: Filter chunks
    filtered = [
        c for c in chunks
        if (not selected_document or c['document'] == selected_document)
        and (not refine_query or refine_query.lower() in c['content'].lower())
    ]

    # Step 2: Basic keyword scoring
    def keyword_score(text, query):
        q_words = query.lower().split()
        text = text.lower()
        return sum(text.count(w) for w in q_words)

    scored = [
        {
            "text": c["content"],
            "document": c["document"],
            "section": c.get("section", "Uncategorised"),
            "score": keyword_score(c["content"], question),
        }
        for c in filtered
    ]

    # Step 3: Select top 20 by keyword
    top = sorted(scored, key=lambda x: x["score"], reverse=True)[:20]

    # Step 4: Semantic rerank if anything was retrieved
    if top:
        q_embed = model.encode(question, convert_to_tensor=True)
        t_embeds = model.encode([c["text"] for c in top], convert_to_tensor=True)
        sims = util.cos_sim(q_embed, t_embeds)[0]

        for i, chunk in enumerate(top):
            chunk["semantic_score"] = float(sims[i])
        top = sorted(top, key=lambda x: x["semantic_score"], reverse=True)

    return top
