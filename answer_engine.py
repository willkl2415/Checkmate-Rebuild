def get_answers(question, chunks, selected_document="", refine_query=""):
    q_words = question.lower().split()

    def score(text):
        return sum(text.lower().count(w) for w in q_words)

    filtered = [
        c for c in chunks
        if (not selected_document or c['document'] == selected_document)
        and (not refine_query or refine_query.lower() in c['content'].lower())
    ]

    results = [
        {
            "content": c["content"],
            "document": c["document"],
            "section": c.get("section", "Uncategorised"),
            "score": score(c["content"]),
        }
        for c in filtered
    ]

    return sorted(results, key=lambda x: x["score"], reverse=True)
