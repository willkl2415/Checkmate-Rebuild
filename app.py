from flask import Flask, render_template, request
import json
from answer_engine import get_answers
import logging
import sys

# Setup debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

app = Flask(__name__)

# Load chunks
with open("chunks.json", "r", encoding="utf-8") as f:
    chunks_data = json.load(f)

@app.route("/", methods=["GET", "POST"])
def index():
    question = ""
    document = "All Documents"
    refine_query = ""
    semantic_mode = False
    answer = []

    # Get all unique document titles
    doc_names = sorted(set(chunk["document"] for chunk in chunks_data if "document" in chunk))
    documents = ["All Documents"] + doc_names

    if request.method == "POST":
        logging.debug("POST received")

        if request.form.get("clear"):
            logging.debug("Clear triggered")
            return render_template("index.html",
                                   question="",
                                   documents=documents,
                                   document="All Documents",
                                   refine_query="",
                                   semantic_mode=False,
                                   answer=[])

        question = request.form.get("question", "")
        document = request.form.get("document", "All Documents")
        refine_query = request.form.get("refine_query", "")
        semantic_mode = request.form.get("semantic") is not None

        logging.debug(f"Question: {question}")
        logging.debug(f"Document: {document}")
        logging.debug(f"Refine: {refine_query}")
        logging.debug(f"Semantic: {semantic_mode}")

        selected_docs = [] if document == "All Documents" else [document]

        answer = get_answers(question, chunks_data, selected_docs, refine_query, semantic_mode)

    return render_template("index.html",
                           question=question,
                           documents=documents,
                           document=document,
                           refine_query=refine_query,
                           semantic_mode=semantic_mode,
                           answer=answer)

if __name__ == "__main__":
    app.run(debug=True)
