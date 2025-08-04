import re
import unicodedata
from langchain.schema import Document


def clean_text(text: str) -> str:
    text = unicodedata.normalize("NFC", text).lower()
    text = re.sub(r"[•●◦■→⇒►◆▪]", " ", text)
    text = re.sub(r"[-–—]{2,}", " ", text)
    text = re.sub(r"\.{2,}", ".", text)
    text = re.sub(r"__+", " ", text)
    text = re.sub(r"[^\w\s\.,:;%/()\[\]-]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def clean_and_filter(docs: list[Document], min_length: int = 50) -> list[Document]:
    """Apply clean_text and drop short pages."""
    out = []
    for doc in docs:
        c = clean_text(doc.page_content)
        if len(c) >= min_length:
            out.append(Document(page_content=c, metadata=doc.metadata))
    return out