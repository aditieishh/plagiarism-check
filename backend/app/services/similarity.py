
import re


def tokenize(text: str) -> set[str]:
    
    words = re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())
    return set(words)


def calculate_similarity(text1: str, text2: str) -> float:
    
    words1 = tokenize(text1)
    words2 = tokenize(text2)

    if not words1 or not words2:
        return 0.0

    common_words = words1 & words2
    all_words = words1 | words2

    return round(len(common_words) / len(all_words) * 100, 2)
