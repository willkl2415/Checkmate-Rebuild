from flask import Flask, render_template, request, jsonify
from answer_engine import get_answers
import json
import os

app = Flask(__name__)

# Load chunks.json
with open('chunks.json', 'r', encoding='utf-8') as f:
    chunks_data = json.load(f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    query = data.get('query', '')
    selected_docs = data.get('selectedDocs', [])
    refine_terms = data.get('refineTerms', '')
    use_semantic = data.get('useSemantic', False)

    print(f"[DEBUG] Query: {query}")
    print(f"[DEBUG] Selected Docs: {selected_docs}")
    print(f"[DEBUG] Refine Terms: {refine_terms}")
    print(f"[DEBUG] Semantic Enabled: {use_semantic}")

    results = get_answers(query, chunks_data, selected_docs, refine_terms, use_semantic)
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
