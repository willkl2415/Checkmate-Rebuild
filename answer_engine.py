from sentence_transformers import SentenceTransformer, util
import logging

# Enable logging
logging.basicConfig(level=logging.DEBUG)

# Load the smart model that understands meaning
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def semantic_search(question, chunks, selected_doc, refine_query):
    logging.debug(f"Semantic search started for: {question}")
    query_embedding = model.encode(question, convert_to_tensor=True)
    matches = []

    for chunk in chunks:
        content = chunk.get("text", "")
        doc_title = chunk.get("document_title", "")
        section = chunk.get("section", "")

        if selected_doc and doc_title != selected_doc:
            continue
        if refine_query and refine_query.lower() not in content.lower():
            continue

        chunk_embedding = model.encode(content, convert_to_tensor=True)
        score = util.pytorch_cos_sim(query_embedding, chunk_embedding).item()

        if score > 0.45:
            matches.append({
                "document": doc_title,
                "section": section,
                "content": content,
                "score": round(score, 3),
                "reason": f"Semantic match with score {round(score, 3)}"
            })

    matches.sort(key=lambda x: x["score"], reverse=True)
    logging.debug(f"Semantic search completed. {len(matches)} matches found.")
    return matches
