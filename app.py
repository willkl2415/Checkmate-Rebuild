from flask import Flask, render_template, request
import json
import logging, sys
from hybrid_engine import get_hybrid_answers  # Uses keyword + rerank pipeline

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
    answer = []

    docs = sorted(set(c.get('document', '') for c in chunks))
    documents = ["All Documents"] + docs

    if request.method == "POST":
        if request.form.get("clear"):
            return render_template("index.html", question="", documents=documents,
                                   document="", refine_query="", answer=[])

        question = request.form.get("question", "")
        document = request.form.get("document", "")
        refine_query = request.form.get("refine_query", "")

        logging.debug(f"Question: {question}")
        logging.debug(f"Document Filter: {document}")
        logging.debug(f"Refine Query: {refine_query}")

        selected = "" if document == "All Documents" else document
        answer = get_hybrid_answers(question, chunks, selected, refine_query)

    return render_template("index.html", question=question, documents=documents,
                           document=document, refine_query=refine_query,
                           answer=answer)

if __name__ == "__main__":
    app.run(debug=True)
