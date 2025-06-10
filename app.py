import json
import re
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Load chunks from JSON
with open("chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

# Define document type priority
def get_priority(doc_title):
    title = doc_title.lower()

    if "jsp 822" in title:
        return 1
    elif "dtsm" in title:
        return 2
    elif "jsp" in title:
        return 3
    elif "mod" in title or "defence" in title:
        return 4
    else:
        return 5

# Search logic
def search_chunks(query):
    query_lower = query.lower()
    results = []

    for chunk in chunks:
        text = chunk.get("text", "")
        if query_lower in text.lower():
            results.append(chunk)

    # Prioritise results by document type
    results.sort(key=lambda x: get_priority(x.get("document_title", "")))

    return results

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search():
    query = request.json.get("query", "")
    document_filter = request.json.get("documentFilter", "")
    section_filter = request.json.get("sectionFilter", "")
    include_subsections = request.json.get("includeSubsections", False)

    results = search_chunks(query)

    # Apply document filter if set
    if document_filter:
        results = [r for r in results if r.get("document_title") == document_filter]

    # Apply section filter
    if section_filter:
        if include_subsections:
            results = [r for r in results if r.get("section", "").startswith(section_filter)]
        else:
            results = [r for r in results if r.get("section", "") == section_filter]

    return jsonify(results)

@app.route("/filters", methods=["GET"])
def filters():
    document_titles = sorted(set(chunk["document_title"] for chunk in chunks if "document_title" in chunk))
    section_titles = sorted(set(chunk["section"] for chunk in chunks if "section" in chunk))

    return jsonify({
        "documents": document_titles,
        "sections": section_titles
    })

if __name__ == "__main__":
    app.run(debug=True)
