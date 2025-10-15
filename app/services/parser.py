from typing import Union
import pdfplumber
import docx

def extract_text(file_path: str) -> str:
    if file_path.lower().endswith(".pdf"):
        return extract_text_pdf(file_path)
    elif file_path.lower().endswith(".docx"):
        return extract_text_docx(file_path)
    else:
        raise ValueError("Unsupported file type. Only PDF and DOCX are supported.")

def extract_text_pdf(file_path: str) -> str:
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def extract_text_docx(file_path: str) -> str:
    doc = docx.Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text
