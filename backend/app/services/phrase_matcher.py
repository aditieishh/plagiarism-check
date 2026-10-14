
import re
from difflib import SequenceMatcher


def split_sentences(text: str) -> list[str]:
    """Split text into sentences and normalize whitespace."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def normalize_sentence(sentence: str) -> str:
    """Lowercase text and remove punctuation for comparison."""
    sentence = sentence.lower()
    sentence = re.sub(r"[^a-z0-9\s]", "", sentence)
    return " ".join(sentence.split())


def find_matching_sentences(
    text1: str,
    text2: str,
    threshold: float = 0.85,
) -> list[dict]:
    """Find identical or highly similar sentences across two texts."""
    sentences1 = split_sentences(text1)
    sentences2 = split_sentences(text2)

    matches = []
    seen = set()

    for sentence1 in sentences1:
        normalized1 = normalize_sentence(sentence1)

        # Ignore very short sentences to reduce meaningless matches.
        if len(normalized1.split()) < 5:
            continue

        for sentence2 in sentences2:
            normalized2 = normalize_sentence(sentence2)

            if len(normalized2.split()) < 5:
                continue

            similarity = SequenceMatcher(
                None,
                normalized1,
                normalized2,
            ).ratio()

            if similarity >= threshold:
                key = (normalized1, normalized2)

                if key not in seen:
                    matches.append({
                        "sentence1": sentence1,
                        "sentence2": sentence2,
                        "similarity_percentage": round(
                            similarity * 100, 2
                        ),
                    })
                    seen.add(key)

    return matches
