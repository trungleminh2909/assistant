# chatbot/setup.py

import os
import shutil
import json

from config import PDF_PATH, POPPLER_PATH, OCR_TEXT_PATH
from .ocr import pdf_to_docs
from .preprocess import clean_and_filter

# 0) sanity-check that pdfinfo is available
_pdfinfo = shutil.which("pdfinfo") or os.path.join(POPPLER_PATH, "pdfinfo")
if not (shutil.which("pdfinfo") or os.path.isfile(_pdfinfo)):
    raise RuntimeError(
        "Poppler ‘pdfinfo’ not found. "
        "Please install poppler or set POPPLER_PATH correctly."
    )

# 1) load or initialize index.json
INDEX_PATH = os.path.join(os.getcwd(), "index.json")
if os.path.exists(INDEX_PATH):
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        index = json.load(f)
else:
    index = {}

_raw_docs = []
to_process = []

# 2) discover all PDFs under PDF_PATH
if os.path.isdir(PDF_PATH):
    pdf_files = [fn for fn in sorted(os.listdir(PDF_PATH))
                 if fn.lower().endswith(".pdf")]
elif PDF_PATH.lower().endswith(".pdf") and os.path.isfile(PDF_PATH):
    pdf_files = [os.path.basename(PDF_PATH)]
else:
    raise RuntimeError(f"PDF_PATH ‘{PDF_PATH}’ is not a directory or .pdf file")

# 3) find newly modified PDFs
for fn in pdf_files:
    full = os.path.join(PDF_PATH, fn)
    mtime = os.path.getmtime(full)
    prev = index.get(fn, {}).get("last_modified", 0)
    if mtime > prev:
        to_process.append((fn, full, mtime))

# 4) if none changed, offer to force re-OCR everything
force_all = False
if not to_process:
    print("[setup] no new or modified PDFs found.")
    if input("Force re-OCR all PDFs? (y/N): ").strip().lower() == "y":
        force_all = True
        to_process = [
            (fn, os.path.join(PDF_PATH, fn), os.path.getmtime(os.path.join(PDF_PATH, fn)))
            for fn in pdf_files
        ]

# 5) now decide whether to OCR the ones in to_process
if to_process:
    if not force_all:
        print(f"[setup] {len(to_process)} new/updated PDFs: {[t[0] for t in to_process]}")
        if input("Re-OCR these files? (y/N): ").strip().lower() != "y":
            print("[setup] skipping OCR for updated files.")
            to_process = []

    if to_process:
        os.makedirs(OCR_TEXT_PATH, exist_ok=True)
        for fn, full, mtime in to_process:
            print(f"[setup] OCR’ing {fn} …")
            docs = pdf_to_docs(full, poppler_path=POPPLER_PATH)

            # dump every page into one .txt with separators
            txt_path = os.path.join(OCR_TEXT_PATH, fn.replace(".pdf", ".txt"))
            with open(txt_path, "w", encoding="utf-8") as tf:
                for i, d in enumerate(docs, start=1):
                    tf.write(f"--- PAGE {i} ---\n")
                    tf.write(d.page_content)
                    tf.write("\n\n")

            # tag & collect documents for indexing
            for d in docs:
                d.metadata["source_file"] = fn
                _raw_docs.append(d)

            # update the timestamp index
            index[fn] = {"last_modified": mtime}

        # persist the updated index.json
        with open(INDEX_PATH, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=2)
else:
    print("[setup] skipping OCR—nothing to do.")

# 6) clean & filter exactly what we just OCR’d
DOCS = clean_and_filter(_raw_docs)
print(f"[setup] ready to index {len(DOCS)} new pages")
