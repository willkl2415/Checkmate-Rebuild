import json
import re

with open("chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

def get_priority(filename):
    name = filename.upper()
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

def keyword_search(query, selected_doc="All Documents"):
    query = query.lower()
    keywords = query.split()

    results = []
    for chunk in chunks:
        doc_name = chunk["document"]
        if selected_doc != "All Documents" and doc_name != selected_doc:
            continue

        text = chunk["content"].lower()
        if all(k in text for k in keywords):
            results.append({
                "document": doc_name,
                "section": chunk.get("section", "Uncategorised"),
                "content": chunk["content"],
                "score": sum(text.count(k) for k in keywords),
                "priority": get_priority(doc_name)
            })

    # Sort by priority first, then by score descending
    sorted_results = sorted(results, key=lambda x: (x["priority"], -x["score"]))
    return sorted_results
