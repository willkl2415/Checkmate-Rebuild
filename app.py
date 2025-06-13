import json
import logging
from flask import Flask, render_template, request
from rapidfuzz import fuzz

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

with open("chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

with open("toc_map.json", "r", encoding="utf-8") as f:
    toc_map = json.load(f)

def get_matches(query, selected_document, refine_query):
    matches = []
    for chunk in chunks:
        if selected_document and chunk["document"] != selected_document:
            continue
        if refine_query and refine_query.lower() not in chunk["content"].lower():
            continue
        score = fuzz.partial_ratio(query.lower(), chunk["content"].lower())
        if score > 60:
            matches.append({
                "content": chunk["content"],
                "document": chunk["document"],
                "section": chunk.get("section", "Uncategorised"),
                "score": score,
            })
    matches.sort(key=lambda x: x["score"], reverse=True)
    return matches[:10]

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    query = ""
    selected_document = ""
    refine_query = ""
    if request.method == "POST":
        query = request.form["query"]
        selected_document = request.form.get("document", "")
        refine_query = request.form.get("refine", "")
        logging.debug(f"Question: {query}")
        logging.debug(f"Document Filter: {selected_document or 'All Documents'}")
        logging.debug(f"Refine Query: {refine_query}")
        results = get_matches(query, selected_document, refine_query)
    documents = sorted(list(set(chunk["document"] for chunk in chunks)))
    return render_template("index.html", results=results, query=query, documents=documents, selected_document=selected_document, refine_query=refine_query, toc_map=toc_map)

if __name__ == "__main__":
    app.run(debug=True)
