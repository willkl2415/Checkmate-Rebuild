import os
import json
import logging
from flask import Flask, render_template, request
from answer_engine import semantic_search

app = Flask(__name__)

# Logging setup
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

# Load document titles
documents = sorted(set(
    c.get("document_title") or c.get("document") for c in chunks
    if c.get("document_title") or c.get("document")
))
logging.debug(f"✅ Extracted {len(documents)} unique document titles.")

@app.route("/", methods=["GET", "POST"])
def index():
    question = ""
    selected_doc = ""
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
        selected_doc = request.form.get("document", "")
        refine_query = request.form.get("refine_query", "").strip()
        semantic_mode = bool(request.form.get("semantic"))

        logging.debug("--- SEARCH DEBUG ---")
        logging.debug(f"Question: {question}")
        logging.debug(f"Selected Document: {selected_doc}")
        logging.debug(f"Refine Query: {refine_query}")
        logging.debug(f"Semantic Mode: {semantic_mode}")

        filtered_chunks = [
            c for c in chunks if
            (selected_doc == "All Documents" or c.get("document_title") == selected_doc or c.get("document") == selected_doc) and
            (not refine_query or refine_query.lower() in c.get("text", "").lower() or refine_query.lower() in c.get("content", "").lower())
        ]

        if semantic_mode:
            answer = semantic_search(question, filtered_chunks, selected_doc, refine_query)
        else:
            q = question.lower()
            answer = [
                {
                    "document": c.get("document_title") or c.get("document"),
                    "section": c.get("section", "Uncategorised"),
                    "content": c.get("text", "") or c.get("content", "")
                }
                for c in filtered_chunks if q in (c.get("text", "") + c.get("content", "")).lower()
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

    return render_template(
        "index.html",
        answer=[],
        question="",
        documents=["All Documents"] + documents,
        selected_doc="All Documents",
        refine_query="",
        semantic_mode=False
    )

if __name__ == "__main__":
    app.run(debug=True)
