import json
from flask import Flask, request, render_template
from answer_engine import semantic_search

app = Flask(__name__)

with open("chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

def get_priority(doc_title):
    title = doc_title.lower()
    if "jsp 822" in title:
        return 1
    elif "dtsm" in title:
        return 2
    elif "jsp" in title:
        return 3
    elif "mod" in title or "defence" in title:
        return 4
    return 5

def filter_chunks_token(question, selected_doc, refine_query):
    if not question:
        return []

    results = []
    for chunk in chunks:
        content = chunk.get("text", "").lower()
        doc_title = chunk.get("document_title", "")
        section = chunk.get("section", "")

        if question.lower() in content:
            if selected_doc and doc_title != selected_doc:
                continue
            if refine_query and refine_query.lower() not in content:
                continue
            results.append({
                "document": doc_title,
                "section": section,
                "content": chunk.get("text", "")
            })

    results.sort(key=lambda x: get_priority(x["document"]))
    return results

@app.route("/", methods=["GET", "POST"])
def index():
    question = ""
    selected_doc = ""
    refine_query = ""
    use_semantic = False
    answer = []

    documents = sorted(set(chunk["document_title"] for chunk in chunks if "document_title" in chunk))

    if request.method == "POST":
        if request.form.get("clear"):
            return render_template("index.html", question="", selected_doc="", refine_query="", documents=documents, answer=[], use_semantic=False)

        question = request.form.get("question", "")
        selected_doc = request.form.get("document", "")
        refine_query = request.form.get("refine_query", "")
        use_semantic = request.form.get("semantic") == "on"

        filtered_chunks = [c for c in chunks if not selected_doc or c.get("document_title") == selected_doc]

        if use_semantic:
            answer = semantic_search(question, filtered_chunks)
        else:
            answer = filter_chunks_token(question, selected_doc, refine_query)

    return render_template("index.html", question=question, selected_doc=selected_doc, refine_query=refine_query, documents=documents, answer=answer, use_semantic=use_semantic)

if __name__ == "__main__":
    app.run(debug=True)
