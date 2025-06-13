def get_answers(question, chunks, selected_document="", refine_query=""):
    """
    Fast keyword-based search only. No embedding, no reranking.
    """

    # Step 1: Filter by document and refine query
    filtered = [
        c for c in chunks
        if (not selected_document or c['document'] == selected_document)
        and (not refine_query or refine_query.lower() in c['content'].lower())
    ]

    # Step 2: Score by keyword presence in content
    def keyword_score(text, query):
        words = query.lower().split()
        text = text.lower()
        return sum(text.count(w) for w in words)

    scored = [
        {
            "text": c["content"],
            "document": c["document"],
            "section": c.get("section", "Uncategorised"),
            "score": keyword_score(c["content"], question),
        }
        for c in filtered
    ]

    # Step 3: Return top 20 by score
    top = sorted(scored, key=lambda x: x["score"], reverse=True)[:20]
    return top
