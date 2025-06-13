import re

def get_answers(question, chunks, selected_doc="", refine_query=""):
    def keyword_score(text, query):
        q_words = query.lower().split()
        text = text.lower()
        return sum(text.count(w) for w in q_words)

    def get_priority(doc_name):
        name = doc_name.lower()
        if "jsp 822" in name:
            return 1
        elif "dtsm" in name:
            return 2
        elif "jsp" in name:
            return 3
        elif "mod" in name or "defence" in name:
            return 4
        else:
            return 5

    # Step 1: Filter based on document and refine query
    filtered = [
        c for c in chunks
        if (not selected_doc or c['document'] == selected_doc)
        and (not refine_query or refine_query.lower() in c['content'].lower())
    ]

    # Step 2: Score and priority tagging
    results = []
    for c in filtered:
        score = keyword_score(c["content"], question)
        if score > 0:
            results.append({
                "document": c["document"],
                "section": c.get("section", ""),
                "content": c["content"],
                "score": score,
                "priority": get_priority(c["document"])
            })

    # Step 3: Sort by priority first, then score
    results_sorted = sorted(results, key=lambda x: (x["priority"], -x["score"]))

    return results_sorted
