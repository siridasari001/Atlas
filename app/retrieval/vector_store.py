import chromadb

from app.models.metadata import KnowledgeChunk


class KnowledgeVectorStore:
    """
    Manage governance and remediation knowledge stored in ChromaDB.
    """

    def __init__(
        self,
        collection_name: str = "atlas_governance",
        persist_directory: str = "data/vector_store",
    ):
        self.client = chromadb.PersistentClient(
            path=persist_directory
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name
        )

    def add_chunks(self, chunks: list[KnowledgeChunk]) -> None:
        if not chunks:
            return

        self.collection.upsert(
            ids=[
                f"{chunk.source}:{chunk.chunk_id}"
                for chunk in chunks
            ],
            documents=[
                chunk.content
                for chunk in chunks
            ],
            metadatas=[
                {
                    "source": chunk.source,
                    "category": chunk.category,
                    "chunk_id": chunk.chunk_id,
                }
                for chunk in chunks
            ],
        )

    def count(self) -> int:
        return self.collection.count()