from flask import Flask, render_template, request
import json
from answer_engine import semantic_search
import logging

# Setup debug logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

with open("chunks.json", "r") as f:
    chunks = json.load(f)

@app.route("/", methods=["GET", "POST"])
def index():
    question = ""
    document = ""
    refine_query = ""
    semantic_mode = False
    answer = []

    documents = sorted(set(chunk["document_title"] for chunk in chunks))

    if request.method == "POST":
        logging.debug("POST received")

        if request.form.get("clear"):
            logging.debug("Clear triggered")
            return render_template("index.html",
                                   question="",
                                   documents=documents,
                                   document="",
                                   refine_query="",
                                   semantic_mode=False,
                                   answer=[])

        question = request.form.get("question", "")
        document = request.form.get("document", "")
        refine_query = request.form.get("refine_query", "")
        semantic_mode = request.form.get("semantic") is not None

        logging.debug(f"Question: {question}")
        logging.debug(f"Document filter: {document}")
        logging.debug(f"Refine query: {refine_query}")
        logging.debug(f"Semantic toggle: {semantic_mode}")

        if semantic_mode:
            logging.debug("Semantic mode activated")
            answer = semantic_search(question, chunks, document, refine_query)
        else:
            logging.debug("Running keyword search fallback")
            for chunk in chunks:
                content = chunk.get("text", "")
                doc_title = chunk.get("document_title", "")
                section = chunk.get("section", "")

                if document and doc_title != document:
                    continue
                if refine_query and refine_query.lower() not in content.lower():
                    continue
                if question.lower() in content.lower():
                    answer.append({
                        "document": doc_title,
                        "section": section,
                        "content": content,
                        "reason": "Direct keyword match"
                    })

    return render_template("index.html",
                           question=question,
                           documents=documents,
                           document=document,
                           refine_query=refine_query,
                           semantic_mode=semantic_mode,
                           answer=answer)

if __name__ == "__main__":
    app.run(debug=True)
