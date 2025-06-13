from flask import Flask, render_template, request
import json
import logging, sys
from answer_engine import get_answers

logging.basicConfig(level=logging.DEBUG, handlers=[logging.StreamHandler(sys.stdout)])
app = Flask(__name__)

# Load chunks once
with open("chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

def document_priority(doc_name):
    name = doc_name.upper()
    if "JSP 822" in name:
        return 1
    elif "DTSM" in name:
        return 2
    elif "JSP" in name and "822" not in name:
        return 3
    elif "MOD" in name or "DEFENCE" in name:
        return 4
    else:
        return 5

@app.route("/", methods=["GET", "POST"])
def index():
    question = ""
    document = ""
    refine_query = ""
    answer = []
    full_result_count = 0

    docs = sorted(set(c.get('document', '') for c in chunks))
    documents = ["All Documents"] + docs

    if request.method == "POST":
        if request.form.get("clear"):
            return render_template("index.html", question="", documents=documents,
                                   document="", refine_query="", answer=[], full_result_count=0)

        question = request.form.get("question", "")
        document = request.form.get("document", "")
        refine_query = request.form.get("refine_query", "")

        logging.debug(f"Question: {question}")
        logging.debug(f"Document Filter: {document}")
        logging.debug(f"Refine Query: {refine_query}")

        selected = "" if document == "All Documents" else document
        answer = get_answers(question, chunks, selected, refine_query)
        full_result_count = len(answer)

        # Apply document priority sorting
        answer.sort(key=lambda x: document_priority(x['document']))

        # Limit to top 10 after priority sort
        answer = answer[:10]

    return render_template("index.html", question=question, documents=documents,
                           document=document, refine_query=refine_query,
                           answer=answer, full_result_count=full_result_count)

if __name__ == "__main__":
    app.run(debug=True)
