from langchain.prompts import PromptTemplate

router_prompt = PromptTemplate.from_template(
    """
Chat history:
{chat_history}

Should this question be answered from the *internal* employee handbook?
- Only answer “yes” if it’s about policies, procedures, benefits, HR, etc.
- Otherwise, answer “no".

Question: {query}
Answer (yes/no):
"""
)

handbook_prompt = PromptTemplate.from_template(
    """
Chat history:
{chat_history}

Use the handbook context below to answer the user question.
Context:
{context}

Question: {question}
Answer:
"""
)

fallback_prompt = PromptTemplate.from_template(
    """
You are a friendly assistant. Use the conversation history to answer naturally.

Chat history:
{chat_history}

User: {question}
Assistant:
"""
)   