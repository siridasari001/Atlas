from pathlib import Path


def load_knowledge_document(file_path: str | Path) -> str:
    """
    Load a Markdown knowledge document.

    Args:
        file_path: Path to the knowledge document.

    Returns:
        The document contents as a string.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Knowledge document not found: {path}")

    if path.suffix.lower() != ".md":
        raise ValueError("Atlas currently supports Markdown knowledge documents only.")

    return path.read_text(encoding="utf-8")