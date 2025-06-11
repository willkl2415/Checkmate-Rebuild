import os
import json
import logging
from flask import Flask, render_template, request
from answer_engine import semantic_search
from utils import load_chunks, load_documents

app = Flask(__name__)

# Load chunks and document titles
CHUNKS_PATH = os.path.join("data", "chunks.json")
chunks = load_chunks(CHUNKS_PATH)
documents = load_documents(chunks)

# Enable logging for debug
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
        selected_doc = request.form.get("document", "")
        refine_query = request.form.get("refine_query", "").strip()
        semantic_mode = True if request.form.get("semantic") == "on" else False

        if not question:
            return render_template(
                "index.html",
                answer=[],
                question=question,
                documents=["All Documents"] + documents,
                selected_doc=selected_doc or "All Documents",
                refine_query=refine_query,
                semantic_mode=semantic_mode
            )

        logging.debug("--- SEARCH DEBUG ---")
        logging.debug(f"Question: {question}")
        logging.debug(f"Selected Document: {selected_doc}")
        logging.debug(f"Refine Query: {refine_query}")
        logging.debug(f"Semantic Mode: {semantic_mode}")

        if semantic_mode:
            answer = semantic_search(
                question,
                selected_doc if selected_doc != "All Documents" else "",
                refine_query
            )
        else:
            # Token search fallback
            answer = []
            q = question.lower()
            for chunk in chunks:
                if selected_doc and selected_doc != "All Documents" and chunk["document_title"] != selected_doc:
                    continue
                if refine_query and refine_query.lower() not in chunk["text"].lower():
                    continue
                if q in chunk["text"].lower():
                    answer.append({
                        "document": chunk["document_title"],
                        "section": chunk["section"],
                        "content": chunk["text"]
                    })

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
