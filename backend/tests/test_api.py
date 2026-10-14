
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_home_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == (
        "PDF Plagiarism Checker API is running"
    )


def test_compare_requires_at_least_two_files():
    response = client.post(
        "/compare",
        files=[
            ("files", ("one.pdf", b"sample content", "application/pdf"))
        ],
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Upload at least two PDF files."


def test_compare_rejects_non_pdf():
    response = client.post(
        "/compare",
        files=[
            ("files", ("one.txt", b"hello", "text/plain")),
            ("files", ("two.pdf", b"sample content", "application/pdf")),
        ],
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Only PDF files are allowed."

def test_compare_rejects_empty_pdf():
    response = client.post(
        "/compare",
        files=[
            ("files", ("empty.pdf", b"", "application/pdf")),
            ("files", ("second.pdf", b"sample content", "application/pdf")),
        ],
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "empty.pdf is empty."


def test_compare_rejects_oversized_pdf():
    from app.main import MAX_FILE_SIZE

    oversized_content = b"x" * (MAX_FILE_SIZE + 1)

    response = client.post(
        "/compare",
        files=[
            ("files", ("large.pdf", oversized_content, "application/pdf")),
            ("files", ("second.pdf", b"sample content", "application/pdf")),
        ],
    )

    assert response.status_code == 413
    assert response.json()["detail"] == "large.pdf exceeds the 5 MB limit."
