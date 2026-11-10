
import chromadb


client = chromadb.PersistentClient(
    path="backend/chroma_db"
)

collection = client.get_or_create_collection(
    name="cruis_policies"
)


def store_embeddings(chunks, embeddings):
    collection.upsert(
        ids=[str(i) for i in range(len(chunks))],
        documents=chunks,
        embeddings=embeddings
    )
