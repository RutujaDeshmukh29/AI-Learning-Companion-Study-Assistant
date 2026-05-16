"""
PDF Loader Module
Handles PDF extraction and text cleaning using PyMuPDF (fitz)
"""

import fitz  # PyMuPDF
import os
import re


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract raw text from a PDF file.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Extracted and cleaned text as a string
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")
    
    doc = fitz.open(file_path)
    full_text = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
        if text.strip():
            full_text.append(f"[Page {page_num + 1}]\n{text}")
    
    doc.close()
    raw_text = "\n\n".join(full_text)
    return clean_text(raw_text)


def clean_text(text: str) -> str:
    """
    Clean and normalize extracted text.
    
    Args:
        text: Raw extracted text
        
    Returns:
        Cleaned text
    """
    # Remove excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    
    # Remove common PDF artifacts
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    
    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Remove lines that are just numbers (page numbers)
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped and not re.match(r'^\d+$', stripped):
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines).strip()


def get_pdf_metadata(file_path: str) -> dict:
    """
    Extract metadata from a PDF file.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Dictionary containing PDF metadata
    """
    doc = fitz.open(file_path)
    metadata = doc.metadata
    page_count = len(doc)
    doc.close()
    
    return {
        "title": metadata.get("title", "Unknown"),
        "author": metadata.get("author", "Unknown"),
        "page_count": page_count,
        "subject": metadata.get("subject", ""),
    }


def save_uploaded_pdf(uploaded_file, save_dir: str = "data/uploaded_pdfs") -> str:
    """
    Save a Streamlit uploaded file to disk.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        save_dir: Directory to save the file
        
    Returns:
        Path to saved file
    """
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, uploaded_file.name)
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return file_path
