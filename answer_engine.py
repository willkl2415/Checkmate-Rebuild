import json

# Load chunks
with open("chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

def get_priority(filename):
    upper = filename.upper()
    if "JSP 822" in upper:
        return 1
    elif "DTSM" in upper:
        return 2
    elif "JSP" in upper:
        return 3
    elif "MOD" in upper or "DEFENCE" in upper:
        return 4
    else:
        return 5

def keyword_search(query, selected_doc="All Documents"):
    query = query.lower().strip()
    keywords = query.split()

    results = []
    for chunk in chunks:
        doc = chunk["document"]
        if selected_doc != "All Documents" and doc != selected_doc:
            continue

        content = chunk["content"].lower()
        if all(k in content for k in keywords):
            results.append({
                "document": doc,
                "section": chunk.get("section", "Uncategorised"),
                "content": chunk["content"],
                "score": sum(content.count(k) for k in keywords),
                "priority": get_priority(doc)
            })

    # Final: priority first, then descending score second
    results = sorted(results, key=lambda x: (x["priority"], -x["score"]))
    return results
