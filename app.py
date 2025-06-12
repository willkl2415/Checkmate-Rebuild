from flask import Flask, render_template, request
import json
from answer_engine import semantic_search

app = Flask(__name__)

# Load chunks of information from the file
with open("chunks.json", "r") as f:
    chunks = json.load(f)

# Home page
@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    question = ""
    selected_doc = ""
    refine_query = ""
    semantic = False

    documents = sorted(set(chunk["document_title"] for chunk in chunks))

    if request.method == "POST":
        question = request.form.get("question", "")
        selected_doc = request.form.get("selected_doc", "")
        refine_query = request.form.get("refine_query", "")
        semantic = request.form.get("semantic") is not None

        if semantic:
            results = semantic_search(question, chunks, selected_doc, refine_query)
        else:
            for chunk in chunks:
                content = chunk.get("text", "")
                doc_title = chunk.get("document_title", "")
                section = chunk.get("section", "")

                if selected_doc and doc_title != selected_doc:
                    continue
                if refine_query and refine_query.lower() not in content.lower():
                    continue
                if question.lower() in content.lower():
                    results.append({
                        "document": doc_title,
                        "section": section,
                        "content": content,
                        "reason": "Direct keyword match"
                    })

    return render_template("index.html",
                           results=results,
                           question=question,
                           documents=documents,
                           selected_doc=selected_doc,
                           refine_query=refine_query,
                           semantic=semantic)

if __name__ == "__main__":
    app.run(debug=True)
