# PDF Plagiarism Checker

A full-stack PDF similarity analysis tool that compares academic assignments to identify matching sentences and potential paraphrases using lexical and semantic similarity detection.

The application allows users to upload multiple PDF documents and view pairwise comparison results, including similarity percentages and highlighted matching passages.

## Features

- **Multiple PDF uploads:** Upload and compare up to 10 PDF files.
- **PDF text extraction:** Extract textual content from uploaded documents.
- **Lexical similarity detection:** Identify matching or closely worded sentences.
- **Semantic similarity analysis:** Use Google Gemini embeddings to identify sentences with similar meanings despite differences in wording.
- **Pairwise comparison:** Analyze each document pair independently.
- **Similarity reports:** View lexical and semantic similarity percentages.
- **Matched passage analysis:** Review corresponding sentences from both documents.
- **Input validation:** Validate PDF file types, file sizes, and minimum upload requirements.
- **REST API:** Process PDF comparison requests through a FastAPI backend.

## Tech Stack

| Component & Technologies |

| Frontend - React.js, JavaScript, CSS |
| Backend - Python, FastAPI |
| Semantic analysis - Google Gemini Embeddings API |
| Numerical computation - NumPy |
| Text similarity - scikit-learn |
| PDF processing - pdfplumber, pypdf |
| API communication - REST API, multipart/form-data |
| Deployment - Render |
| Version control - Git, GitHub |

## How It Works

1. The user uploads two or more PDF assignments.
2. The frontend sends the files to the FastAPI backend.
3. The backend extracts text from the uploaded PDFs.
4. The extracted text is processed to identify sentences and compare their wording.
5. Google Gemini embeddings represent sentences as numerical vectors for semantic comparison.
6. The system calculates lexical and semantic similarity scores and identifies potential sentence matches.
7. The API returns the comparison results as JSON.
8. The frontend displays a report containing document pairs, similarity scores, and matching passages.

## Architecture


                 React Frontend
                       |
                       | PDF uploads
                       | multipart/form-data
                       v
                 FastAPI Backend
                       |
                       v
                 PDF Text Extraction
                       |
              +--------+--------+
              |                 |
              v                 v
       Lexical Matching   Gemini Embeddings
              |                 |
              |                 v
              |        Semantic Similarity
              |                 |
              +--------+--------+
                       |
                       v
                Comparison Results
                       |
                       v
                React Results Page
