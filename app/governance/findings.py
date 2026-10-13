from app.models.metadata import AtlasFinding


def find_finding(
    findings: list[AtlasFinding],
    column: str | None = None,
    issue: str | None = None,
) -> AtlasFinding | None:
    """
    Find the first AtlasFinding matching the provided criteria.

    Args:
        findings: List of normalized AtlasFinding objects.
        column: Optional column name to match.
        issue: Optional issue name to match.

    Returns:
        The first matching AtlasFinding, or None if no match exists.
    """

    for finding in findings:
        if column is not None and finding.column != column:
            continue

        if issue is not None and finding.issue != issue:
            continue

        return finding

    return None