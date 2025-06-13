from rapidfuzz import fuzz

def document_priority(name):
    name = name.lower()
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

def get_answers(question, chunks, selected_doc="", refine_query=""):
    # Step 1: Filter
    filtered = [
        c for c in chunks
        if (not selected_doc or c['document'] == selected_doc)
        and (not refine_query or refine_query.lower() in c['content'].lower())
    ]

    # Step 2: Score and classify priority
    for c in filtered:
        c["score"] = fuzz.partial_ratio(question.lower(), c["content"].lower())
        c["priority"] = document_priority(c["document"])

    # Step 3: Sort by priority then score (descending)
    sorted_chunks = sorted(filtered, key=lambda x: (x["priority"], -x["score"]))

    return sorted_chunks
