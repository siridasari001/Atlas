import pandas as pd

from app.models.metadata import QualityFinding


def detect_missing_values(df: pd.DataFrame) -> list[QualityFinding]:
    """
    Detect columns containing missing values.

    Args:
        df: Pandas DataFrame to inspect.

    Returns:
        A list of findings for columns with missing values.
    """

    findings: list[QualityFinding] = []

    for column in df.columns:
        missing_count = int(df[column].isna().sum())

        if missing_count > 0:
            findings.append(
                QualityFinding(
                    column=column,
                    issue="missing_values",
                    count=missing_count,
                    severity="medium",
                    description=f"Column '{column}' contains missing values.",
                )
            )

    return findings


def detect_duplicates(df: pd.DataFrame) -> list[QualityFinding]:
    """
    Detect duplicate records in a dataset.

    Args:
        df: Pandas DataFrame to inspect.

    Returns:
        A list of findings for duplicate records.
    """

    duplicate_count = int(df.duplicated().sum())

    if duplicate_count == 0:
        return []

    return [
        QualityFinding(
            column=None,
            issue="duplicate_records",
            count=duplicate_count,
            severity="high",
            description="The dataset contains duplicate records.",
        )
    ]


def detect_invalid_values(df: pd.DataFrame) -> list[QualityFinding]:
    """
    Detect invalid values based on business rules.

    Args:
        df: Pandas DataFrame to inspect.

    Returns:
        A list of findings for invalid values.
    """

    findings: list[QualityFinding] = []

    if "annual_spend" in df.columns:
        invalid_count = int((df["annual_spend"] < 0).sum())

        if invalid_count > 0:
            findings.append(
                QualityFinding(
                    column="annual_spend",
                    issue="invalid_negative_value",
                    count=invalid_count,
                    severity="high",
                    description="Annual spend cannot contain negative values.",
                )
            )

    return findings