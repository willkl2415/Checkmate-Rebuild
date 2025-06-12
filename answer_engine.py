import re
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def clean(text):
    return re.sub(r'\s+', ' ', text.replace('\n', ' ')).strip()

def get_answers(query, chunks_data, selected_docs, refine_terms, use_semantic):
    results = []

    if use_semantic:
        print("[DEBUG] Using semantic search")
        query_embedding = model.encode(query, convert_to_tensor=True)

        for chunk in chunks_data:
            doc_name = chunk.get('document', '')
            section = chunk.get('section', '')
            content = chunk.get('content', '')

            if selected_docs and doc_name not in selected_docs:
                continue
            if refine_terms and refine_terms.lower() not in content.lower():
                continue

            chunk_embedding = model.encode(content, convert_to_tensor=True)
            similarity = util.pytorch_cos_sim(query_embedding, chunk_embedding).item()

            results.append({
                'document': doc_name,
                'section': section,
                'text': clean(content),
                'score': similarity
            })

        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:10]

    else:
        print("[DEBUG] Using keyword search")
        q = query.lower()
        for chunk in chunks_data:
            doc_name = chunk.get('document', '')
            section = chunk.get('section', '')
            content = chunk.get('content', '')

            if selected_docs and doc_name not in selected_docs:
                continue
            if refine_terms and refine_terms.lower() not in content.lower():
                continue
            if q in content.lower():
                results.append({
                    'document': doc_name,
                    'section': section,
                    'text': clean(content),
                    'score': 1.0
                })

        return results[:10]
