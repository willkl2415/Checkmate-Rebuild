def get_answers(question, chunks, selected_document="", refine_query=""):
    def keyword_score(text, query):
        q_words = query.lower().split()
        text = text.lower()
        return sum(text.count(w) for w in q_words)

    def get_priority(doc_name):
        name = doc_name.upper()
        if "JSP 822" in name:
            return 1
        elif "DTSM" in name:
            return 2
        elif "JSP" in name:
            return 3
        elif "MOD" in name or "DEFENCE" in name:
            return 4
        else:
            return 5

    # Step 1: Base filter
    filtered = [
        c for c in chunks
        if (not selected_document or c['document'] == selected_document)
        and (not refine_query or refine_query.lower() in c['content'].lower())
    ]

    # Step 2: Score + priority
    scored = [
        {
            "content": c["content"],
            "document": c["document"],
            "section": c.get("section", "Uncategorised"),
            "score": keyword_score(c["content"], question),
            "priority": get_priority(c["document"])
        }
        for c in filtered
    ]

    # Step 3: Sort by priority only (ignore score for now)
    sorted_chunks = sorted(scored, key=lambda x: x["priority"])

    return sorted_chunks
