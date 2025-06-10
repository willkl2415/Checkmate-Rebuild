import json
import re
from flask import Flask, request, render_template

app = Flask(__name__)

# Load chunks from file
with open("chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

# Define priority order
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

# Filter and search logic with diagnostics
def filter_chunks(question, selected_doc, refine_query):
    if not question:
        print("No question provided.")
        return []

    results = []
    question_pattern = re.compile(rf"\b{re.escape(question.strip())}\b", re.IGNORECASE)
    refine_pattern = re.compile(rf"\b{re.escape(refine_query.strip())}\b", re.IGNORECASE) if refine_query else None

    print(f"\n--- SEARCH DEBUG ---")
    print(f"Question: {question}")
    print(f"Selected Document: {selected_doc}")
    print(f"Refine Query: {refine_query}\n")

    for i, chunk in enumerate(chunks):
        content = chunk.get("text", "")
        doc_title = chunk.get("document_title", "")
        section = chunk.get("section", "")

        match_q = question_pattern.search(content)
        match_r = refine_pattern.search(content) if refine_pattern else True
        match_d = (doc_title == selected_doc) if selected_doc else True

        if match_q and match_r and match_d:
            print(f"✓ Match #{len(results) + 1}: {doc_title} — {section}")
            results.append({
                "document": doc_title,
                "section": section,
                "content": content
            })

    if not results:
        print("⚠️ No matches found.")

    results.sort(key=lambda x: get_priority(x["document"]))
    return results

@app.route("/", methods=["GET", "POST"])
def index():
    question = ""
    selected_doc = ""
    refine_query = ""
    answer = []

    documents = sorted(set(chunk["document_title"] for chunk in chunks if "document_title" in chunk))

    if request.method == "POST":
        question = request.form.get("question", "")
        selected_doc = request.form.get("document", "")
        refine_query = request.form.get("refine_query", "")
        answer = filter_chunks(question, selected_doc, refine_query)

    return render_template("index.html", question=question, selected_doc=selected_doc, refine_query=refine_query, documents=documents, answer=answer)

if __name__ == "__main__":
    app.run(debug=True)
