# answer_engine.py

import re
import torch
from sentence_transformers import SentenceTransformer, util
from semantic_query_optimizer import optimise_semantic_query

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def clean_snippet(text):
    return re.sub(r'\s+', ' ', text.replace('\n', ' ')).strip()

def answer_with_semantic(variants, chunks, selected_doc, refine_query):
    print("[DEBUG] Running Optimised Semantic Matching")

    # Pre-filter chunks first
    filtered_chunks = []
    for c in chunks:
        doc = c.get('document', '')
        if selected_doc and doc != selected_doc:
            continue
        content = c.get('content', '')
        if refine_query and refine_query.lower() not in content.lower():
            continue
        filtered_chunks.append(c)

    print(f"[DEBUG] Chunks after filter: {len(filtered_chunks)}")
    if not filtered_chunks:
        return []

    max_chunks = 150  # Safe cap for render stability
    filtered_chunks = filtered_chunks[:max_chunks]
    texts = [c.get('content', '') for c in filtered_chunks]
    chunk_embeddings = model.encode(texts, convert_to_tensor=True)

    results = []
    seen_chunks = set()

    for i, variant in enumerate(variants):
        print(f"[DEBUG] Variant {i+1}: {variant}")
        query_embedding = model.encode(variant, convert_to_tensor=True)
        similarities = util.pytorch_cos_sim(query_embedding, chunk_embeddings)[0]

        for idx, score_tensor in enumerate(similarities):
            score = score_tensor.item()
            if score > 0.45:
                chunk_id = f"{filtered_chunks[idx]['document']}|{filtered_chunks[idx]['section']}|{idx}"
                if chunk_id in seen_chunks:
                    continue
                seen_chunks.add(chunk_id)

                results.append({
                    'document': filtered_chunks[idx].get('document', ''),
                    'section': filtered_chunks[idx].get('section', ''),
                    'text': clean_snippet(filtered_chunks[idx].get('content', '')),
                    'score': round(score, 3),
                    'reason': f"Semantic match from variant {i+1} (score {round(score, 3)})"
                })

    results.sort(key=lambda x: x['score'], reverse=True)
    return results

def answer_with_keyword(query, chunks, selected_doc, refine_query):
    q = query.lower()
    results = []
    for c in chunks:
        doc = c.get('document', '')
        if selected_doc and doc != selected_doc:
            continue
        content = c.get('content', '')
        if refine_query and refine_query.lower() not in content.lower():
            continue
        if q in content.lower():
            results.append({
                'document': doc,
                'section': c.get('section', ''),
                'text': clean_snippet(content),
                'score': 1.0,
                'reason': "Keyword match"
            })
    return results

def get_answers(question, chunks, selected_doc, refine_query, use_semantic):
    if use_semantic:
        print(f"[DEBUG] Running Semantic Matching")
        variants = optimise_semantic_query(question)
        print(f"[DEBUG] Semantic Variants: {variants}")
        return answer_with_semantic(variants, chunks, selected_doc, refine_query)
    else:
        print(f"[DEBUG] Running Keyword Matching")
        return answer_with_keyword(question, chunks, selected_doc, refine_query)
