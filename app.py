import json
from flask import Flask, request, render_template
from answer_engine import semantic_search

app = Flask(__name__)

# Load chunks
with open("data/chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

# Priority sort
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
    else:
        return 5

# Token-based search
def token_match(question, selected_doc, refine_query):
    results = []
    q = question.lower().strip() if question else ""
    r = refine_query.lower().strip() if refine_query else ""

    for chunk in chunks:
        content = chunk.get("text", "").lower()
        doc_title = chunk.get("document_title", "")
        section = chunk.get("section", "")

        match_q = q in content if q else True
        match_r = r in content if r else True
        match_d = doc_title == selected_doc if selected_doc else True

        if match_q and match_r and match_d:
            results.append({
                "document": doc_title,
                "section": section,
                "content": chunk.get("text", ""),
                "score": "n/a",
                "reason": "token match"
            })

    results.sort(key=lambda x: get_priority(x["document"]))
    return results

@app.route("/", methods=["GET", "POST"])
def index():
    question = ""
    selected_doc = ""
    refine_query = ""
    answer = []
    use_semantic = False

    documents = sorted(set(chunk["document_title"] for chunk in chunks if "document_title" in chunk))

    if request.method == "POST":
        question = request.form.get("question", "")
        selected_doc = request.form.get("document", "")
        refine_query = request.form.get("refine_query", "")
        use_semantic = request.form.get("semantic_toggle") == "on"

        if use_semantic:
            filtered_chunks = [c for c in chunks if (not selected_doc or c["document_title"] == selected_doc)]
            answer = semantic_search(filtered_chunks, question)
        else:
            answer = token_match(question, selected_doc, refine_query)

    return render_template("index.html",
        question=question,
        selected_doc=selected_doc,
        refine_query=refine_query,
        documents=documents,
        answer=answer,
        use_semantic=use_semantic
    )

if __name__ == "__main__":
    app.run(debug=True)
