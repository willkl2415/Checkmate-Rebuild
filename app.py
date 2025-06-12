from flask import Flask, render_template, request
import json
from answer_engine import semantic_search

app = Flask(__name__)

# Load the chunks of information from chunks.json
with open("chunks.json", "r") as f:
    chunks = json.load(f)

@app.route("/", methods=["GET", "POST"])
def index():
    question = ""
    document = ""
    refine_query = ""
    answer = []

    # Extract all document titles from the chunks
    documents = sorted(set(chunk["document_title"] for chunk in chunks))

    if request.method == "POST":
        # If user clicked "Clear Search", reset everything
        if request.form.get("clear"):
            return render_template("index.html",
                                   question="",
                                   documents=documents,
                                   document="",
                                   refine_query="",
                                   semantic_mode=True,
                                   answer=[])

        # Capture the question, document filter, and refine query
        question = request.form.get("question", "")
        document = request.form.get("document", "")
        refine_query = request.form.get("refine_query", "")

        # ✅ Always perform Semantic Matching
        answer = semantic_search(question, chunks, document, refine_query)

    # Return the page with search results
    return render_template("index.html",
                           question=question,
                           documents=documents,
                           document=document,
                           refine_query=refine_query,
                           semantic_mode=True,
                           answer=answer)

if __name__ == "__main__":
    app.run(debug=True)
