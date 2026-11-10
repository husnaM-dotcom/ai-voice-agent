
from backend.app.rag.vector_store import collection
from backend.app.rag.embeddings import client


def retrieve_relevant_chunks(question, top_k=3):
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=question,
        config={
            "task_type": "RETRIEVAL_QUERY"
        }
    )

    question_embedding = result.embeddings[0].values

    search_results = collection.query(
        query_embeddings=[question_embedding],
        n_results=top_k
    )

    documents = search_results["documents"][0]
    distances = search_results["distances"][0]

    relevant_chunks = []

    for document, distance in zip(documents, distances):
        print("Distance:", distance)
        print("Document:", document[:100])
        print("-" * 40)

        if distance <= 0.65:
            relevant_chunks.append(document)

    return relevant_chunks

