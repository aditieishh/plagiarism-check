
import re
from functools import lru_cache

from sentence_transformers import SentenceTransformer, util


@lru_cache(maxsize=1)
def load_model():
    """Load the model once and reuse it."""
    return SentenceTransformer("all-MiniLM-L6-v2")


def split_into_sentences(text: str) -> list[str]:
    """Split text into sentences and ignore short fragments."""
    if not text or not text.strip():
        return []

    sentences = re.split(r"(?<=[.!?])\s+", text.strip())

    return [
        sentence.strip()
        for sentence in sentences
        if len(sentence.split()) >= 5
    ][:100]


def calculate_semantic_similarity(
    text1: str,
    text2: str,
) -> float:
    """Calculate document-level semantic similarity as a percentage."""
    sentences1 = split_into_sentences(text1)
    sentences2 = split_into_sentences(text2)

    if not sentences1 or not sentences2:
        return 0.0

    model = load_model()

    embeddings1 = model.encode(
        sentences1,
        convert_to_tensor=True,
        normalize_embeddings=True,
    )
    embeddings2 = model.encode(
        sentences2,
        convert_to_tensor=True,
        normalize_embeddings=True,
    )

    similarity_matrix = util.cos_sim(embeddings1, embeddings2)

    # Best matching sentence in document 2 for every sentence in document 1.
    best_matches1 = similarity_matrix.max(dim=1).values

    # Best matching sentence in document 1 for every sentence in document 2.
    best_matches2 = similarity_matrix.max(dim=0).values

    score = (
        best_matches1.mean().item()
        + best_matches2.mean().item()
    ) / 2

    # Clamp the result to the range 0–100.
    return round(max(0.0, min(1.0, score)) * 100, 2)



def find_semantic_matches(
    text1: str,
    text2: str,
    threshold: float = 0.65,
) -> list[dict]:
    """
    Find strong semantic sentence pairs without reusing sentences.

    The threshold is a cosine similarity value between -1 and 1.
    A threshold of 0.65 means candidate matches must score at least 65
    on the returned percentage scale.
    """
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must be between 0.0 and 1.0")

    sentences1 = split_into_sentences(text1)
    sentences2 = split_into_sentences(text2)

    if not sentences1 or not sentences2:
        return []

    model = load_model()

    embeddings1 = model.encode(
        sentences1,
        convert_to_tensor=True,
        normalize_embeddings=True,
    )
    embeddings2 = model.encode(
        sentences2,
        convert_to_tensor=True,
        normalize_embeddings=True,
    )

    similarity_matrix = util.cos_sim(embeddings1, embeddings2)

    # Collect every candidate pair above the threshold.
    candidates = []

    for i, sentence1 in enumerate(sentences1):
        for j, sentence2 in enumerate(sentences2):
            score = similarity_matrix[i, j].item()

            if score >= threshold:
                candidates.append({
                    "index1": i,
                    "index2": j,
                    "sentence1": sentence1,
                    "sentence2": sentence2,
                    "similarity_score": round(score * 100, 2),
                })

    # Consider the strongest candidate pairs first.
    candidates.sort(
        key=lambda match: match["similarity_score"],
        reverse=True,
    )

    matches = []
    used_sentences1 = set()
    used_sentences2 = set()

    # Greedily select pairs without reusing either sentence.
    for candidate in candidates:
        i = candidate["index1"]
        j = candidate["index2"]

        if i in used_sentences1 or j in used_sentences2:
            continue

        matches.append({
            "sentence1": candidate["sentence1"],
            "sentence2": candidate["sentence2"],
            "similarity_score": candidate["similarity_score"],
        })

        used_sentences1.add(i)
        used_sentences2.add(j)

    return matches
