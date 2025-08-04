import numpy as np
from pdf2image import convert_from_path
import easyocr
from langchain.schema import Document

def pdf_to_docs(pdf_path: str, poppler_path: str) -> list[Document]:
    """
    Convert PDF pages to text Documents via OCR.
    """
    images = convert_from_path(pdf_path, poppler_path=poppler_path)
    reader = easyocr.Reader(['vi'], gpu=True)
    docs = []
    for i, img in enumerate(images):
        lines = reader.readtext(np.array(img), detail=0, paragraph=True)
        text = "\n".join(lines).strip()
        if text:
            docs.append(Document(page_content=text, metadata={"page": i+1}))
    return docs