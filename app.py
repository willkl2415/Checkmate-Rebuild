from flask import Flask, request, render_template
import json
import logging
from answer_engine import semantic_search

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

try:
    with open("data/chunks.json", "r", encoding="utf-8") as f:
        chunks = json.load(f)
    logging.debug(f"✅ Loaded {len(chunks)} chunks.")
except Exception as e:
    logging.error(f"❌ Failed to load chunks.json: {e}")
    chunks = []

documents = ["All Documents"] + sorted(set(c["document"] for c in chunks if "document" in c))

@app.route("/", methods=["GET", "POST"])
def index():
    question = ""
    selected_doc = "All Documents"
    refine_query = ""
    answer = []
    use_semantic = False

    if request.method == "POST":
        if request.form.get("clear"):
            return render_template("index.html", answer=[], question="", documents=documents,
                                   selected_doc="All Documents", refine_query="", use_semantic=False)

        question = request.form.get("question", "").strip()
        selected_doc = request.form.get("document", "All Documents").strip()
        refine_query = request.form.get("refine_query", "").strip()
        use_semantic = bool(request.form.get("semantic"))

        logging.debug("--- SEARCH DEBUG ---")
        logging.debug(f"Question: {question}")
        logging.debug(f"Selected Document: {selected_doc}")
        logging.debug(f"Refine Query: {refine_query}")
        logging.debug(f"Semantic Mode: {use_semantic}")

        filtered = [c for c in chunks if
                    (selected_doc == "All Documents" or c["document"] == selected_doc) and
                    (not refine_query or refine_query.lower() in c["content"].lower())]

        if use_semantic:
            answer = semantic_search(question, filtered, selected_doc, refine_query)
            logging.debug(f"Semantic search returned {len(answer)} results.")
        else:
            answer = [c for c in filtered if question.lower() in c["content"].lower()]
            logging.debug(f"Token search found {len(answer)} matches.")

    return render_template("index.html", answer=answer, question=question, documents=documents,
                           selected_doc=selected_doc, refine_query=refine_query, use_semantic=use_semantic)

if __name__ == "__main__":
    app.run(debug=True)
