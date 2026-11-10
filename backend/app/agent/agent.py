
from google.genai import types

from backend.app.rag.embeddings import client
from backend.app.rag.retriever import retrieve_relevant_chunks


def answer_customer_question(question):
    relevant_chunks = retrieve_relevant_chunks(question)

    if not relevant_chunks:
        return (
            "I’m sorry, but I can’t confirm that information "
            "from our current policies. Let me connect you "
            "with a CRUIS team member who can help."
        )

    context = "\n\n".join(relevant_chunks
    )

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=f"""
You are a friendly customer support assistant for CRUIS
car rental company.

Answer the customer's question using ONLY the policy
information provided below.

Rules:
- Do not invent or assume company policies.
- If the information is insufficient, say you cannot
  confirm and offer human assistance.
- Keep answers clear, natural and concise.

CRUIS POLICY INFORMATION:
{context}

CUSTOMER QUESTION:
{question}
""",
        config=types.GenerateContentConfig(
            temperature=0.2
        )
    )

    return response.text
