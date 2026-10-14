import re
from io import BytesIO
from pypdf import PdfReader


def extract_text_from_pdf(file_bytes: bytes) -> str:
    
    reader = PdfReader(BytesIO(file_bytes))

    pages = []
    for page in reader.pages:
        page_text= page.extract_text() or ""
        pages.append(page_text)

    text = "\n".join(pages)

    # Replace repeated whitespace and line breaks with single spaces.
    text = re.sub(r"\s+", " ", text)

    return text.strip()

