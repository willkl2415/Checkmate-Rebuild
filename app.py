from flask import Flask, render_template, request
import json
import logging, sys
from answer_engine import get_answers

logging.basicConfig(level=logging.DEBUG, handlers=[logging.StreamHandler(sys.stdout)])
app = Flask(__name__)

# Load chunks once
with open("chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

@app.route("/", methods=["GET", "POST"])
def index():
    question = ""
    document = ""
    refine_query = ""
    semantic_mode = False
    answer = []

    docs = sorted(set(c.get('document', '') for c in chunks))
    documents = ["All Documents"] + docs

    if request.method == "POST":
        if request.form.get("clear"):
            return render_template("index.html", question="", documents=documents,
                                   document="", refine_query="",
                                   semantic_mode=False, answer=[])

        question = request.form.get("question", "")
        document = request.form.get("document", "")
        refine_query = request.form.get("refine_query", "")
        semantic_mode = (request.form.get("semantic") is not None)

        logging.debug(f"Question: {question}")
        logging.debug(f"Document Filter: {document}")
        logging.debug(f"Refine Query: {refine_query}")
        logging.debug(f"Semantic Mode: {semantic_mode}")

        selected = "" if document == "All Documents" else document
        answer = get_answers(question, chunks, selected, refine_query, semantic_mode)

    return render_template("index.html", question=question, documents=documents,
                           document=document, refine_query=refine_query,
                           semantic_mode=semantic_mode, answer=answer)

if __name__ == "__main__":
    app.run(debug=True)
