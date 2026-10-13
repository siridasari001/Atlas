from app.retrieval.retriever import KnowledgeRetriever
from app.retrieval.vector_store import KnowledgeVectorStore


def test_retrieve_duplicate_customer_records():

    vector_store = KnowledgeVectorStore()

    retriever = KnowledgeRetriever(
        vector_store
    )

    results = retriever.search(
        query=(
            "duplicate customer records "
            "customer ID uniqueness"
        ),
        top_k=3,
        category="data_integrity",
    )

    assert len(results) > 0

    contents = [
        result["content"]
        for result in results
    ]

    combined_content = " ".join(contents)

    assert "Customer ID Uniqueness" in combined_content
    assert "duplicate" in combined_content.lower()


def test_retrieve_negative_annual_spend():

    vector_store = KnowledgeVectorStore()

    retriever = KnowledgeRetriever(
        vector_store
    )

    results = retriever.search(
        query=(
            "negative annual spend "
            "invalid annual_spend values"
        ),
        top_k=3,
        category="data_quality",
    )

    assert len(results) > 0

    contents = [
        result["content"]
        for result in results
    ]

    combined_content = " ".join(contents)

    assert "Annual Spend" in combined_content
    assert "negative" in combined_content.lower()


def test_retrieve_remediation_for_negative_spend():

    vector_store = KnowledgeVectorStore()

    retriever = KnowledgeRetriever(
        vector_store
    )

    results = retriever.search(
        query=(
            "approved remediation for "
            "negative annual spend"
        ),
        top_k=3,
        category="remediation",
    )

    assert len(results) > 0

    contents = [
        result["content"]
        for result in results
    ]

    combined_content = " ".join(contents)

    assert "Negative Annual Spend" in combined_content
    assert "data owner" in combined_content.lower()