from flask import Flask, render_template, request
import json
import logging, sys

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

    # All unique documents for dropdown
    docs = sorted(set(c.get('document', '') for c in chunks))
    documents = ["All Documents"] + docs

    if request.method == "POST":
        if request.form.get("clear"):
            return render_template("index.html", question="", documents=documents,
                                   document="", refine_query="", answer=[])

        question = request.form.get("question", "").strip()
        document = request.form.get("document", "")
        refine_query = request.form.get("refine_query", "").strip()

        logging.debug(f"Question: {question}")
        logging.debug(f"Document Filter: {document}")
        logging.debug(f"Refine Query: {refine_query}")

        selected = "" if document == "All Documents" else document

        def keyword_score(text, query):
            q_words = query.lower().split()
            text = text.lower()
            return sum(text.count(w) for w in q_words)

        # Filter by document + refine query
        filtered = [
            c for c in chunks
            if (not selected or c['document'] == selected)
            and (not refine_query or refine_query.lower() in c['content'].lower())
        ]

        logging.debug(f"Chunks after filter: {len(filtered)}")

        # Score everything
        answer = [
            {
                "document": c["document"],
                "section": c.get("section", "Uncategorised"),
                "content": c["content"],
                "score": keyword_score(c["content"], question)
            }
            for c in filtered
            if keyword_score(c["content"], question) > 0
        ]

        # Sort highest to lowest by score
        answer = sorted(answer, key=lambda x: x["score"], reverse=True)

    return render_template("index.html", question=question, documents=documents,
                           document=document, refine_query=refine_query, answer=answer)

if __name__ == "__main__":
    app.run(debug=True)
