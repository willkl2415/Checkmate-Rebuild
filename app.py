import os
import json
import logging
from flask import Flask, render_template, request
from answer_engine import semantic_search

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

# Load chunks
CHUNKS_PATH = os.path.join("data", "chunks.json")
try:
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    logging.debug(f"✅ Loaded {len(chunks)} chunks.")
except Exception as e:
    logging.error(f"❌ Failed to load chunks.json: {e}")
    chunks = []

# Extract documents
documents = sorted(set(c["document_title"] for c in chunks if "document_title" in c))
logging.debug(f"✅ Found {len(documents)} unique documents: {documents}")

@app.route("/", methods=["GET", "POST"])
def index():
    question = ""
    selected_doc = "All Documents"
    refine_query = ""
    semantic_mode = False
    answer = []

    if request.method == "POST":
        if request.form.get("clear"):
            return render_template(
                "index.html",
                answer=[],
                question="",
                documents=["All Documents"] + documents,
                selected_doc="All Documents",
                refine_query="",
                semantic_mode=False
            )

        question = request.form.get("question", "").strip()
        selected_doc = request.form.get("document", "All Documents")
        refine_query = request.form.get("refine_query", "").strip()
        semantic_mode = request.form.get("semantic") == "on"

        logging.debug("--- SEARCH DEBUG ---")
        logging.debug(f"Question: {question}")
        logging.debug(f"Selected Document: {selected_doc}")
        logging.debug(f"Refine Query: {refine_query}")
        logging.debug(f"Semantic Mode: {semantic_mode}")

        filtered = [
            c for c in chunks
            if (selected_doc == "All Documents" or c.get("document_title") == selected_doc)
            and (not refine_query or refine_query.lower() in c.get("text", "").lower())
        ]

        if semantic_mode:
            answer = semantic_search(question, filtered, selected_doc, refine_query)
        else:
            q = question.lower()
            answer = [
                {
                    "document": c.get("document_title", ""),
                    "section": c.get("section", ""),
                    "content": c.get("text", "")
                }
                for c in filtered if q in c.get("text", "").lower()
            ]
            logging.debug(f"Token search found {len(answer)} matches.")

    return render_template(
        "index.html",
        answer=answer,
        question=question,
        documents=["All Documents"] + documents,
        selected_doc=selected_doc,
        refine_query=refine_query,
        semantic_mode=semantic_mode
    )

if __name__ == "__main__":
    app.run(debug=True)
