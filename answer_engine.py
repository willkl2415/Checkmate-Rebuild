# answer_engine.py

from rapidfuzz import fuzz

def get_answers(question, chunks, selected_doc="", refine_query=""):
    """
    Retrieve and rank chunks based on a question and optional filters.
    Applies fuzzy scoring and sorts globally by score in descending order.
    """

    def apply_filters(c):
        # Document match
        if selected_doc and c["document"] != selected_doc:
            return False
        # Refine text match
        if refine_query and refine_query.lower() not in c["content"].lower():
            return False
        return True

    def score_chunk(content):
        return fuzz.partial_ratio(question.lower(), content.lower())

    # Apply filters first
    filtered = [c for c in chunks if apply_filters(c)]

    # Apply scoring
    for c in filtered:
        c["score"] = score_chunk(c["content"])

    # Sort all scored chunks globally by descending score
    sorted_chunks = sorted(filtered, key=lambda x: x["score"], reverse=True)

    # Return all results (no artificial slicing)
    return sorted_chunks
