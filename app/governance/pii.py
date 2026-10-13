import pandas as pd

from app.models.metadata import PIIClassification, PII_COLUMNS


def detect_pii_columns(df: pd.DataFrame) -> list[PIIClassification]:
    findings: list[PIIClassification] = []

    for column in df.columns:
        if column.lower() in PII_COLUMNS:
            findings.append(
                PIIClassification(
                    column=column,
                    classification="PII",
                    reason=(
                        f"Column '{column}' may contain "
                        "personally identifiable information."
                    ),
                )
            )

    return findings