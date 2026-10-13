from app.models.metadata import AtlasFinding, PII_COLUMNS


def sanitize_evidence(
    evidence: list[dict],
    finding: AtlasFinding,
) -> list[dict]:
    """
    Remove or redact sensitive fields from evidence before it is
    passed to downstream components such as the LLM or UI.

    Args:
        evidence: Raw evidence records collected from the dataset.
        finding: The Atlas finding associated with the evidence.

    Returns:
        Sanitized evidence records.
    """

    sanitized_evidence: list[dict] = []

    for item in evidence:
        sanitized_row = {}

        for column, value in item["row_data"].items():

            if column.lower() in PII_COLUMNS:
                sanitized_row[column] = "[REDACTED]"
            else:
                sanitized_row[column] = value

        item_column = item.get("column")

        if item_column is None:
            sanitized_value = None
        elif item_column.lower() in PII_COLUMNS:
            sanitized_value = "[REDACTED]"
        else:
            sanitized_value = item["value"]

        sanitized_evidence.append(
            {
                "row_index": item["row_index"],
                "column": item_column,
                "value": sanitized_value,
                "row_data": sanitized_row,
            }
        )

    return sanitized_evidence