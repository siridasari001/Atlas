import pandas as pd

from app.models.metadata import AtlasFinding


def collect_finding_evidence(
    df: pd.DataFrame,
    finding: AtlasFinding,
) -> list[dict]:
    """
    Collect concrete dataset evidence supporting an AtlasFinding.

    Args:
        df: Dataset being analyzed.
        finding: Normalized AtlasFinding.

    Returns:
        A list of dictionaries containing relevant rows and values.
    """

    evidence: list[dict] = []

    # --------------------------------------------------
    # Duplicate records
    # --------------------------------------------------

    if finding.issue == "duplicate_records":
        duplicate_mask = df.duplicated(keep=False)
        matching_rows = df[duplicate_mask]

        for index, row in matching_rows.iterrows():
            row_data = {}

            for field, value in row.items():
                if pd.isna(value):
                    row_data[field] = None
                else:
                    row_data[field] = value

            evidence.append(
                {
                    "row_index": int(index),
                    "column": None,
                    "value": None,
                    "row_data": row_data,
                }
            )

        return evidence

    # --------------------------------------------------
    # Column-specific findings
    # --------------------------------------------------

    if finding.column is None:
        return []

    column = finding.column

    if column not in df.columns:
        return []

    # --------------------------------------------------
    # Missing values
    # --------------------------------------------------

    if finding.issue == "missing_values":
        matching_rows = df[df[column].isna()]

    # --------------------------------------------------
    # Invalid negative values
    # --------------------------------------------------

    elif finding.issue == "invalid_negative_value":
        matching_rows = df[df[column] < 0]

    # --------------------------------------------------
    # Behavioral anomalies
    # --------------------------------------------------

    elif finding.issue == "behavioral_anomaly":
        series = df[column].dropna()

        # Avoid unreliable statistics on very small samples.
        if len(series) < 5:
            return []

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1

        if iqr == 0:
            return []

        lower_bound = q1 - (1.5 * iqr)
        upper_bound = q3 + (1.5 * iqr)

        anomaly_mask = (
            (df[column] < lower_bound)
            | (df[column] > upper_bound)
        )

        matching_rows = df[anomaly_mask]

    # --------------------------------------------------
    # PII findings
    # --------------------------------------------------

    elif finding.issue == "pii_detected":
        matching_rows = df[df[column].notna()]

    # --------------------------------------------------
    # Unknown finding type
    # --------------------------------------------------

    else:
        return []

    # --------------------------------------------------
    # Convert matching rows into evidence records
    # --------------------------------------------------

    for index, row in matching_rows.iterrows():
        row_data = {}

        for field, value in row.items():
            if pd.isna(value):
                row_data[field] = None
            else:
                row_data[field] = value

        evidence.append(
            {
                "row_index": int(index),
                "column": column,
                "value": row_data.get(column),
                "row_data": row_data,
            }
        )

    return evidence