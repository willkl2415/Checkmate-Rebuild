# answer_engine.py

def get_answers(question, chunks, selected_doc="", refine_query=""):
    def keyword_score(text, query):
        q_words = query.lower().split()
        text = text.lower()
        return sum(text.count(w) for w in q_words)

    def doc_priority(name):
        name_upper = name.upper()
        if "JSP 822" in name_upper:
            return 1
        elif "DTSM" in name_upper:
            return 2
        elif "JSP" in name_upper:
            return 3
        elif "MOD" in name_upper or "DEFENCE" in name_upper:
            return 4
        else:
            return 5

    results = []
    for c in chunks:
        if selected_doc and c["document"] != selected_doc:
            continue
        if refine_query and refine_query.lower() not in c["content"].lower():
            continue

        results.append({
            "document": c["document"],
            "section": "" if c.get("section", "").upper() == "UNCATEGORISED" else c.get("section", ""),
            "content": c["content"],
            "score": keyword_score(c["content"], question),
            "priority": doc_priority(c["document"]),
        })

    # ✅ Sort strictly by priority only
    sorted_results = sorted(results, key=lambda x: x["priority"])

    return sorted_results
