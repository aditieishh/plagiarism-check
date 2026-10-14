import pytest

from app.services.semantic_similarity import find_semantic_matches
from app.services.semantic_similarity import (
    calculate_semantic_similarity,
    find_semantic_matches,
    split_into_sentences,
)


def test_split_into_sentences():
    text = (
        "Machine learning helps computers learn patterns from data. "
        "The weather is pleasant today."
    )

    sentences = split_into_sentences(text)

    assert len(sentences) == 2


def test_empty_text_returns_zero_similarity():
    assert calculate_semantic_similarity("", "") == 0.0


def test_empty_text_returns_no_semantic_matches():
    matches = find_semantic_matches("", "")

    assert matches == []


def test_paraphrased_sentences_are_matched():
    text1 = (
        "Machine learning enables computers to learn patterns from data "
        "and make predictions without being explicitly programmed "
        "for every task."
    )

    text2 = (
        "Computers can identify patterns in information and predict "
        "outcomes using machine learning, rather than requiring "
        "instructions for each individual task."
    )

    matches = find_semantic_matches(
        text1,
        text2,
        threshold=0.65,
    )

    assert len(matches) > 0
    assert matches[0]["similarity_score"] >= 65


def test_unrelated_sentences_have_no_high_confidence_match():
    text1 = (
        "The football team scored several goals during the final "
        "match of the tournament."
    )

    text2 = (
        "Fresh vegetables should be stored carefully inside "
        "the refrigerator to maintain their quality."
    )

    matches = find_semantic_matches(
        text1,
        text2,
        threshold=0.80,
    )

    assert matches == []

def test_semantic_matches_do_not_reuse_sentences():
    text1 = (
        "Machine learning helps computers identify patterns in data. "
        "Artificial intelligence allows machines to perform complex tasks."
    )

    text2 = (
        "Machine learning discovers useful patterns from information. "
        "Artificial intelligence helps computers perform difficult tasks."
    )

    matches = find_semantic_matches(
        text1,
        text2,
        threshold=0.65,
    )

    sentences1 = [match["sentence1"] for match in matches]
    sentences2 = [match["sentence2"] for match in matches]

    assert len(sentences1) == len(set(sentences1))
    assert len(sentences2) == len(set(sentences2))


def test_semantic_matching_rejects_invalid_threshold():
    with pytest.raises(ValueError):
        find_semantic_matches(
            "Machine learning helps computers learn patterns from data.",
            "Computers identify patterns in information using machine learning.",
            threshold=1.5,
        )
