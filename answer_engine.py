# answer_engine.py

import re
import logging

# Priority keywords for result ordering
def priority_rank(doc_name):
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

# Simple keyword scoring (counts overlap words)
def keyword_score(text, query):
    query_words = query.lower().split()
    text = text.lower()
    return sum(text.count(word) for word in query_words)

def get_answers(question, chunks, selected_doc="", refine_query=""):
    results = []

    # Step 1: Initial filter by selected document
    filtered_chunks = [
        c for c in chunks
        if selected_doc in ["", "All Documents"] or c.get("document", "") == selected_doc
    ]

    # Step 2: Apply keyword scoring to question
    for c in filtered_chunks:
        score = keyword_score(c.get("content", ""), question)
        if score > 0:
            results.append({
                "document": c.get("document", "Unknown"),
                "section": c.get("section", "Uncategorised"),
                "content": c.get("content", ""),
                "score": score,
                "priority": priority_rank(c.get("document", ""))
            })

    # Step 3: Apply refine_query if given
    if refine_query:
        refine_lower = refine_query.lower()
        results = [
            r for r in results if refine_lower in r["content"].lower()
        ]

    # Step 4: Final sort — by priority (asc), score (desc)
    results.sort(key=lambda r: (r["priority"], -r["score"]))

    return results
