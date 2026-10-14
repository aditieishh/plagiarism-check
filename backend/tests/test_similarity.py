
from app.services.similarity import calculate_similarity


def test_identical_text():
    assert calculate_similarity("Java Python", "Java Python") == 100.0


def test_no_common_words():
    assert calculate_similarity("Java Python", "Apple Mango") == 0.0


def test_partial_similarity():
    assert calculate_similarity("Java Python", "Java React") == 33.33


def test_empty_text():
    assert calculate_similarity("", "Java Python") == 0.0
