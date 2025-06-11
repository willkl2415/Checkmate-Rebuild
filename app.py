import os
import json
import logging
from flask import Flask, render_template, request
from answer_engine import semantic_search

app = Flask(__name__)

# Load chunks.json
with open("data/chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

# Extract document list from chunks
documents = sorted(list(set(chunk.get("document", "") for chunk in chunks if "document" in chunk)))

# Enable logging
logging.basicConfig(level=logging.DEBUG)

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
        selected_doc = request.form.get("document", "All Documents")
        refine_query = request.form.get("refine_query", "").strip()
        semantic_mode = bool(request.form.get("semantic"))

        logging.debug("--- SEARCH DEBUG ---")
        logging.debug(f"Question: {question}")
        logging.debug(f"Selected Document: {selected_doc}")
        logging.debug(f"Refine Query: {refine_query}")
        logging.debug(f"Semantic Mode: {semantic_mode}")

        # Filter chunks
        filtered = [chunk for chunk in chunks if
                    (selected_doc == "All Documents" or chunk.get("document") == selected_doc) and
                    (not refine_query or refine_query.lower() in chunk.get("text", "").lower())]

        if semantic_mode:
            answer = semantic_search(question, filtered, selected_doc, refine_query)
        else:
            q = question.lower()
            answer = [chunk for chunk in filtered if q in chunk.get("text", "").lower()]
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
