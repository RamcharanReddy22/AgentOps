import chromadb
from chromadb.config import Settings

chroma_client = chromadb.PersistentClient(
    path="/home/ubuntu/agentops/vector_db",
    settings=Settings(anonymized_telemetry=False)
)

collection = chroma_client.get_or_create_collection(name="market_docs")

def add_documents(texts: list[str], ids: list[str]):
    # Only add documents that don't already exist
    existing = collection.get(ids=ids)
    existing_ids = set(existing["ids"])
    new_texts = []
    new_ids = []
    for text, id in zip(texts, ids):
        if id not in existing_ids:
            new_texts.append(text)
            new_ids.append(id)
    if new_texts:
        collection.add(documents=new_texts, ids=new_ids)
        print(f"Added {len(new_texts)} new document chunks")
    else:
        print("All chunks already exist, skipping")

def search_documents(query: str, n_results: int = 4) -> list[str]:
    try:
        results = collection.query(query_texts=[query], n_results=n_results)
        docs = results.get("documents", [[]])[0]
        return docs if docs else ["No relevant documents found."]
    except Exception as e:
        return ["No relevant documents found."]
