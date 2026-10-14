
import os
import re
from functools import lru_cache

import numpy as np
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = "gemini-embedding-001"
BATCH_SIZE = 50


@lru_cache(maxsize=1)
def get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")
    return genai.Client(api_key=api_key)


def split_into_sentences(text: str) -> list[str]:
    if not text or not text.strip():
        return []

    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [
        sentence.strip()
        for sentence in sentences
        if len(sentence.split()) >= 5
    ][:100]


def _get_embeddings(sentences: list[str]) -> np.ndarray:
    client = get_client()
    all_embeddings = []

    for start in range(0, len(sentences), BATCH_SIZE):
        batch = sentences[start:start + BATCH_SIZE]

        response = client.models.embed_content(
            model=MODEL_NAME,
            contents=batch,
            config=types.EmbedContentConfig(
                task_type="SEMANTIC_SIMILARITY",
                output_dimensionality=768,
            ),
        )

        if not response.embeddings:
            raise RuntimeError("Gemini returned no embeddings.")

        all_embeddings.extend(
            embedding.values for embedding in response.embeddings
        )

    embeddings = np.asarray(all_embeddings, dtype=np.float32)
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    return embeddings / np.maximum(norms, 1e-12)


def _similarity_matrix(
    sentences1: list[str],
    sentences2: list[str],
) -> np.ndarray:
    # Embed both groups in the same request sequence.
    embeddings = _get_embeddings(sentences1 + sentences2)
    split_at = len(sentences1)

    return embeddings[:split_at] @ embeddings[split_at:].T


def calculate_semantic_similarity(
    text1: str,
    text2: str,
) -> float:
    sentences1 = split_into_sentences(text1)
    sentences2 = split_into_sentences(text2)

    if not sentences1 or not sentences2:
        return 0.0

    similarity = _similarity_matrix(sentences1, sentences2)
    score = (
        similarity.max(axis=1).mean()
        + similarity.max(axis=0).mean()
    ) / 2

    return round(float(np.clip(score, 0.0, 1.0)) * 100, 2)


def find_semantic_matches(
    text1: str,
    text2: str,
    threshold: float = 0.65,
) -> list[dict]:
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must be between 0.0 and 1.0")

    sentences1 = split_into_sentences(text1)
    sentences2 = split_into_sentences(text2)

    if not sentences1 or not sentences2:
        return []

    similarity = _similarity_matrix(sentences1, sentences2)
    rows, cols = np.where(similarity >= threshold)

    candidates = sorted(
        zip(rows.tolist(), cols.tolist()),
        key=lambda pair: similarity[pair[0], pair[1]],
        reverse=True,
    )

    matches = []
    used1, used2 = set(), set()

    for i, j in candidates:
        if i in used1 or j in used2:
            continue

        used1.add(i)
        used2.add(j)

        matches.append({
            "sentence1": sentences1[i],
            "sentence2": sentences2[j],
            "similarity_score": round(
                float(similarity[i, j]) * 100, 2
            ),
        })

    return matches
