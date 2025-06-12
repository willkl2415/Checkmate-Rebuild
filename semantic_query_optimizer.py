# semantic_query_optimizer.py

import re

# Known DSAT keyword expansions
KSA_EXPANSIONS = ["knowledge, skills, and attitudes", "KSAs"]
GAP_ANALYSIS_TERMS = [
    "training needs analysis",
    "gap assessment",
    "training gap identification",
    "training deficiency evaluation"
]

# Phrase mappings for common "How" queries
TRANSFORMATIONS = [
    (r"\bhow do I (perform|conduct|carry out|do)\b", "steps to"),
    (r"\bhow do I\b", "steps to"),
    (r"\bwhat is the process for\b", "process for"),
    (r"\bhow can I\b", "methods to"),
    (r"\bcan I\b", "ways to"),
    (r"\bhow\b", "process to"),
]

def expand_keywords(query):
    expanded = [query]

    # Expand KSAs
    if "KSA" in query or "KSAs" in query:
        expanded += [query.replace("KSAs", alt).replace("KSA", alt) for alt in KSA_EXPANSIONS]

    # Expand gap analysis
    if "gap analysis" in query or "training gap" in query:
        for alt in GAP_ANALYSIS_TERMS:
            expanded.append(query.replace("gap analysis", alt).replace("training gap", alt))

    return list(set(expanded))


def optimise_semantic_query(query: str) -> list:
    """
    Transforms and expands a query for improved semantic search results.
    Returns a list of semantically expanded queries.
    """
    clean = query.strip().lower()

    # Apply transformations for conversational phrasing
    for pattern, replacement in TRANSFORMATIONS:
        clean = re.sub(pattern, replacement, clean)

    # Expand keywords contextually
    expanded_queries = expand_keywords(clean)

    return expanded_queries

