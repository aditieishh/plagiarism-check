
from app.services.phrase_matcher import find_matching_sentences


def test_identical_sentences_are_matched():
    text = (
        "Object oriented programming allows developers "
        "to reuse code through inheritance."
    )

    matches = find_matching_sentences(text, text)

    assert len(matches) == 1
    assert matches[0]["similarity_percentage"] == 100.0


def test_different_sentences_are_not_matched():
    text1 = (
        "Python supports powerful data analysis tools "
        "for scientific computing."
    )

    text2 = (
        "The weather today is sunny and pleasant "
        "for everyone outside."
    )

    matches = find_matching_sentences(text1, text2)

    assert matches == []


def test_short_sentences_are_ignored():
    matches = find_matching_sentences("Hello world.", "Hello world.")

    assert matches == []
