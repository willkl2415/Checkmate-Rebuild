import json
import torch
import logging
from sentence_transformers import SentenceTransformer, util

# Enable debug logs
logging.basicConfig(level=logging.DEBUG)

# Load model
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Global store for chunks with embeddings
CHUNKS_WITH_EMBEDDINGS = []

def encode_chunks(chunks):
    """Precompute and store chunk embeddings at startup."""
    logging.debug("Encoding all document chunks...")
    for chunk in chunks:
        text = chunk.get("text", "")
        embedding = model.encode(text, convert_to_tensor=True)
        CHUNKS_WITH_EMBEDDINGS.append({
            "document": chunk.get("document_title", ""),
            "section": chunk.get("section", ""),
            "text": text,
            "embedding": embedding
        })
    logging.debug(f"Encoded {len(CHUNKS_WITH_EMBEDDINGS)} chunks.")

def semantic_search(question, selected_doc, refine_query):
    """Perform semantic search using precomputed chunk embeddings."""
    logging.debug(f"Semantic search started for: {question}")
    query_embedding = model.encode(question, convert_to_tensor=True)
    matches = []

    for entry in CHUNKS_WITH_EMBEDDINGS:
        if selected_doc and selected_doc != "All Documents" and entry["document"] != selected_doc:
            continue
        if refine_query and refine_query.lower() not in entry["text"].lower():
            continue

        score = util.pytorch_cos_sim(query_embedding, entry["embedding"]).item()
        if score > 0.45:
            matches.append({
                "document": entry["document"],
                "section": entry["section"],
                "content": entry["text"],
                "score": round(score, 3),
                "reason": f"Semantic match with score {round(score, 3)}"
            })

    matches.sort(key=lambda x: x["score"], reverse=True)
    logging.debug(f"Semantic search completed. {len(matches)} matches found.")
    return matches
