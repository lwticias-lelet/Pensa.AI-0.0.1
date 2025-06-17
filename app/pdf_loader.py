import os
import fitz  # PyMuPDF
from llama_index.core.schema import Document

def load_pdfs_from_folder(folder_path):
    documents = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            filepath = os.path.join(folder_path, filename)
            text = extract_text_from_pdf(filepath)
            documents.append(Document(text=text, metadata={"filename": filename}))

    return documents

def extract_text_from_pdf(filepath):
    doc = fitz.open(filepath)
    text = ""
    for page in doc:
        text += page.get_text()
    return text
