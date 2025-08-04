import os
from dotenv import load_dotenv
# Paths & API keys
load_dotenv()   # read .env

PDF_PATH     = os.getenv("PDF_PATH")
OCR_TEXT_PATH  = os.getenv("OCR_TEXT_PATH")
PROCESSED_PATH  = os.getenv("PROCESSED_PATH")
STORE_PATH      = os.getenv("STORE_PATH")
POPPLER_PATH = os.getenv("POPPLER_PATH")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Embedding & retrieval parameters
EMBEDDING_MODEL = "models/embedding-001"
RETRIEVAL_K = 15
SCORE_THRESHOLD = 0.5

# LLM settings
LLM_MODEL = "gemini-2.5-flash"
LLM_TEMPERATURE = 0.3