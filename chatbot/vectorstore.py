import os
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from config import (
    EMBEDDING_MODEL,
    GOOGLE_API_KEY,
    RETRIEVAL_K,
    SCORE_THRESHOLD,
    STORE_PATH,
)

# ensure the API key
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

def build_retriever(docs: list) -> any:
    """
    Builds or loads a persistent FAISS index in STORE_PATH/vectorstore/.
    - First run: creates index folder, indexes `docs` and saves.
    - Later runs: loads index, adds new docs (if any), and re‐saves.
    """
    emb = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)

    # ensure base store directory exists
    os.makedirs(STORE_PATH, exist_ok=True)
    index_dir = os.path.join(STORE_PATH, "vectorstore")

    if os.path.exists(index_dir):
        # load existing index, allow dangerouse deserialization to load from file
        db = FAISS.load_local(
            index_dir,
            emb,
            allow_dangerous_deserialization=True
        )
        if docs:
            db.add_documents(docs)
            db.save_local(index_dir)
    else:
        # build brand‐new index
        db = FAISS.from_documents(docs, emb)
        db.save_local(index_dir)

    return db.as_retriever(search_kwargs={
        "k": RETRIEVAL_K,
        "score_threshold": SCORE_THRESHOLD,
    })
