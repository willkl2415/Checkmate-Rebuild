from flask import Flask, request, render_template, jsonify
import json
import logging
from search_engine import get_top_matches

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

with open("chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

@app.route("/")
def index():
    documents = sorted(list(set(c["document"] for c in chunks)))
    return render_template("index.html", documents=documents)

@app.route("/search", methods=["POST"])
def search():
    data = request.get_json()
    question = data.get("question", "")
    selected_document = data.get("document", "")
    refine_query = data.get("refine_query", "")
    include_subsections = data.get("include_subsections", False)

    logging.debug(f"Question: {question}")
    logging.debug(f"Document Filter: {selected_document}")
    logging.debug(f"Refine Query: {refine_query}")
    logging.debug(f"Include Subsections: {include_subsections}")

    results = get_top_matches(question, chunks, selected_document, refine_query, include_subsections)
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)
