from app.retrieval.vector_store import KnowledgeVectorStore


class KnowledgeRetriever:
    """
    Retrieve relevant governance and remediation knowledge
    from the Atlas vector store.
    """

    def __init__(self, vector_store: KnowledgeVectorStore):
        self.vector_store = vector_store

    def search(
        self,
        query: str,
        top_k: int = 3,
        distance_threshold: float = 1.2,
        category: str | None = None,
    ) -> list[dict]:
        """
        Retrieve relevant knowledge chunks.

        Args:
            query: Natural-language search query.
            top_k: Maximum number of chunks to retrieve.
            distance_threshold: Maximum allowed vector distance.
            category: Optional knowledge category filter.

        Returns:
            Relevant knowledge chunks.
        """

        where_filter = None

        if category is not None:
            where_filter = {
                "category": category,
            }

        results = self.vector_store.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where_filter,
        )

        retrieved_chunks = []

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances,
        ):
            if distance > distance_threshold:
                continue

            retrieved_chunks.append(
                {
                    "content": document,
                    "source": metadata.get("source"),
                    "category": metadata.get("category"),
                    "chunk_id": metadata.get("chunk_id"),
                    "distance": distance,
                }
            )

        return retrieved_chunks