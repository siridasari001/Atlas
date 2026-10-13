from app.models.metadata import KnowledgeChunk


def chunk_markdown_document(
    document: str,
    source: str,
) -> list[KnowledgeChunk]:
    """
    Split a Markdown knowledge document into logical rule-based chunks.
    """

    sections = document.split("\n---\n")

    chunks: list[KnowledgeChunk] = []

    for index, section in enumerate(sections, start=1):
        section = section.strip()

        if not section:
            continue

        category = "governance"

        # Determine the knowledge category from the source file.
        if "remediation" in source.lower():
            category = "remediation"

        # Determine more specific governance categories.
        elif "PII" in section:
            category = "pii"

        elif (
            "annual_spend" in section
            or "Missing Customer Information" in section
        ):
            category = "data_quality"

        elif "Customer ID" in section:
            category = "data_integrity"

        chunks.append(
            KnowledgeChunk(
                content=section,
                source=source,
                chunk_id=index,
                category=category,
            )
        )

    return chunks