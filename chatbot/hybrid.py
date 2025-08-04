from .chains import get_router_chain, get_handbook_chain, get_fallback_chain
from .setup import DOCS
from .vectorstore import build_retriever

# Initialize once
router_chain = get_router_chain()
retriever = build_retriever(DOCS)
handbook_chain = get_handbook_chain(retriever)
fallback_chain = get_fallback_chain()


def hybrid_chatbot(query: str) -> str:
    """Route question through handbook or fallback."""
    decision = router_chain.run(query=query).strip().lower()
    if "yes" in decision:
        return handbook_chain.run(question=query)
    return fallback_chain.run(question=query)