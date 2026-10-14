
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Annotated
from fastapi.openapi.utils import get_openapi

from fastapi.middleware.cors import CORSMiddleware

from app.services.pdf_extractor import extract_text_from_pdf
from app.services.similarity import calculate_similarity
from app.services.phrase_matcher import find_matching_sentences
from app.services.semantic_similarity import (
    calculate_semantic_similarity,
    find_semantic_matches,
)



app = FastAPI(title="PDF Plagiarism Checker")

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version="0.1.0",
        routes=app.routes,
    )

    schema["openapi"] = "3.0.3"

    request_schema = schema["paths"]["/compare"]["post"]["requestBody"][
        "content"
    ]["multipart/form-data"]["schema"]

    body_name = request_schema["$ref"].split("/")[-1]
    body_schema = schema["components"]["schemas"][body_name]

    body_schema["properties"]["files"] = {
        "type": "array",
        "title": "Files",
        "items": {
            "type": "string",
            "format": "binary",
        },
    }

    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_FILE_SIZE = 5 * 1024 * 1024
MAX_FILES = 10


class ComparisonResult(BaseModel):
    file1: str
    file2: str
    similarity_percentage: float
    semantic_similarity_percentage: float | None
    matching_sentences: list[dict]
    semantic_matches: list[dict]


@app.get("/")
def home():
    return {
        "message": "PDF Plagiarism Checker API is running"
    }


@app.post("/compare", response_model=list[ComparisonResult])
async def compare_pdfs( files: Annotated[list[UploadFile], File(description="Upload two or more PDF files")]):
    # Validate the number of uploaded files.
    if len(files) < 2:
        raise HTTPException(
            status_code=400,
            detail="Upload at least two PDF files.",
        )

    if len(files) > MAX_FILES:
        raise HTTPException(
            status_code=400,
            detail=f"You can upload a maximum of {MAX_FILES} PDF files.",
        )

    documents = []

    # Read and validate each PDF.
    for uploaded_file in files:
        if not uploaded_file.filename:
            raise HTTPException(
                status_code=400,
                detail="Every uploaded file must have a filename.",
            )

        # Validate the file extension.
        if not uploaded_file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are allowed.",
            )

        file_bytes = await uploaded_file.read()

        # Reject empty uploads before attempting PDF extraction.
        if not file_bytes:
            raise HTTPException(
                status_code=400,
                detail=f"{uploaded_file.filename} is empty.",
            )

        # Reject files larger than 5 MB.
        if len(file_bytes) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"{uploaded_file.filename} exceeds the 5 MB limit.",
            )

        # Extract text from the PDF.
        try:
            extracted_text = extract_text_from_pdf(file_bytes)
        except Exception as exc:
            raise HTTPException(
                status_code=400,
                detail=f"Could not read {uploaded_file.filename} as a PDF.",
            ) from exc

        # Reject PDFs without extractable text.
        if not extracted_text.strip():
            raise HTTPException(
                status_code=400,
                detail=(
                    f"No extractable text found in {uploaded_file.filename}. "
                    "Scanned PDFs may require OCR."
                ),
            )

        documents.append({
            "filename": uploaded_file.filename,
            "text": extracted_text,
        })

    results = []

    # Compare every unique pair of documents.
    for i in range(len(documents)):
        for j in range(i + 1, len(documents)):
            document1 = documents[i]
            document2 = documents[j]

            text1 = document1["text"]
            text2 = document2["text"]

            # Calculate word-based similarity.
            word_similarity = calculate_similarity(text1, text2)

            # Calculate overall semantic similarity.
            semantic_similarity = calculate_semantic_similarity(
                text1,
                text2,
            )

            # Find similar sentences using the existing phrase matcher.
            phrase_matches = find_matching_sentences(text1, text2)

            # Find semantically similar sentences, including paraphrases.
            semantic_matches = find_semantic_matches(
                text1,
                text2,
                threshold=0.65,
            )

            results.append(
                ComparisonResult(
                    file1=document1["filename"],
                    file2=document2["filename"],
                    similarity_percentage=word_similarity,
                    semantic_similarity_percentage=semantic_similarity,
                    matching_sentences=phrase_matches,
                    semantic_matches=semantic_matches,
                )
            )

    return results
