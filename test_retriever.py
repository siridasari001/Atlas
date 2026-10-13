from app.retrieval.retriever import KnowledgeRetriever
from app.retrieval.vector_store import KnowledgeVectorStore


vector_store = KnowledgeVectorStore()

retriever = KnowledgeRetriever(vector_store)

query = "Why was annual_spend flagged as invalid?"

results = retriever.search(query, top_k=3)

print(f"\nQuery: {query}")
print(f"Retrieved chunks: {len(results)}")

for result in results:
    print("\n--- Retrieved Chunk ---")
    print(f"Chunk ID: {result['chunk_id']}")
    print(f"Category: {result['category']}")
    print(f"Distance: {result['distance']}")
    print(f"Source: {result['source']}")
    print(result["content"])