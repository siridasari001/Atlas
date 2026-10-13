from app.retrieval.vector_store import KnowledgeVectorStore
from app.retrieval.loader import load_knowledge_document
from app.retrieval.chunker import chunk_markdown_document


knowledge_path = "data/knowledge/governance_rules.md"

knowledge = load_knowledge_document(knowledge_path)

chunks = chunk_markdown_document(
    knowledge,
    knowledge_path,
)

vector_store = KnowledgeVectorStore()

vector_store.add_chunks(chunks)

print(f"Knowledge chunks stored: {vector_store.count()}")