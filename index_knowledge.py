from app.retrieval.loader import load_knowledge_document
from app.retrieval.chunker import chunk_markdown_document
from app.retrieval.vector_store import KnowledgeVectorStore


KNOWLEDGE_FILES = [
    "data/knowledge/governance_rules.md",
    "data/knowledge/remediation_rules.md",
]


vector_store = KnowledgeVectorStore()


for knowledge_path in KNOWLEDGE_FILES:
    print(f"\nLoading: {knowledge_path}")

    document = load_knowledge_document(
        knowledge_path
    )

    chunks = chunk_markdown_document(
        document=document,
        source=knowledge_path,
    )

    print(f"Chunks created: {len(chunks)}")

    vector_store.add_chunks(chunks)


print("\n=== ATLAS KNOWLEDGE INDEX ===")
print(f"Total chunks in vector store: {vector_store.count()}")