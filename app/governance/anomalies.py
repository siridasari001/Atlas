import pandas as pd

from app.models.metadata import QualityFinding


def detect_numeric_anomalies(
    df: pd.DataFrame,
) -> list[QualityFinding]:
    """
    Detect unusual values in numeric columns using
    the Interquartile Range (IQR) method.

    A value is considered anomalous when it falls below
    Q1 - 1.5 * IQR or above Q3 + 1.5 * IQR.

    Columns with fewer than 5 non-null values are skipped
    because statistical anomaly detection is unreliable on
    extremely small samples.
    """

    findings: list[QualityFinding] = []

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns

    for column in numeric_columns:
        series = df[column].dropna()

        # Avoid unreliable statistics on very small samples.
        if len(series) < 5:
            continue

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)

        iqr = q3 - q1

        if iqr == 0:
            continue

        lower_bound = q1 - (1.5 * iqr)
        upper_bound = q3 + (1.5 * iqr)

        anomaly_mask = (
            (df[column] < lower_bound)
            | (df[column] > upper_bound)
        )

        anomaly_count = int(anomaly_mask.sum())

        if anomaly_count == 0:
            continue

        findings.append(
            QualityFinding(
                column=column,
                issue="behavioral_anomaly",
                count=anomaly_count,
                severity="medium",
                description=(
                    f"Column '{column}' contains "
                    f"{anomaly_count} value(s) outside the "
                    f"expected statistical range based on "
                    f"the IQR method. "
                    f"Expected range: "
                    f"{lower_bound:.2f} to "
                    f"{upper_bound:.2f}."
                ),
            )
        )

    return findings