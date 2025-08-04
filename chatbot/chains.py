from langchain.chains import LLMChain, ConversationalRetrievalChain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from .prompts import router_prompt, handbook_prompt, fallback_prompt

from config import LLM_MODEL, LLM_TEMPERATURE

# Shared memory
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Initialize LLM
llm = ChatGoogleGenerativeAI(model=LLM_MODEL, temperature=LLM_TEMPERATURE)

# Chains
def get_router_chain() -> LLMChain:
    return LLMChain(llm=llm, prompt=router_prompt, memory=memory)


def get_handbook_chain(retriever) -> ConversationalRetrievalChain:
    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={"prompt": handbook_prompt},
        return_source_documents=False
    )


def get_fallback_chain() -> LLMChain:
    return LLMChain(llm=llm, prompt=fallback_prompt, memory=memory)