import pandas as pd

from app.governance.anomalies import detect_numeric_anomalies
from app.governance.pii import detect_pii_columns
from app.governance.quality import (
    detect_duplicates,
    detect_invalid_values,
    detect_missing_values,
)
from app.models.metadata import AtlasFinding


def analyze_dataset(df: pd.DataFrame) -> dict:
    """
    Run all deterministic governance and data-quality checks
    and normalize the results into a common AtlasFinding structure.

    Args:
        df: Pandas DataFrame to analyze.

    Returns:
        A dictionary containing categorized findings and
        a unified list of AtlasFinding objects.
    """

    quality_findings = detect_missing_values(df)
    duplicate_findings = detect_duplicates(df)
    invalid_findings = detect_invalid_values(df)
    pii_findings = detect_pii_columns(df)
    anomaly_findings = detect_numeric_anomalies(df)

    all_findings: list[AtlasFinding] = []

    # Normalize data-quality findings
    for finding in quality_findings:
        all_findings.append(
            AtlasFinding(
                category="data_quality",
                column=finding.column,
                issue=finding.issue,
                count=finding.count,
                severity=finding.severity,
                description=finding.description,
            )
        )

    # Normalize duplicate findings
    for finding in duplicate_findings:
        all_findings.append(
            AtlasFinding(
                category="data_integrity",
                column=finding.column,
                issue=finding.issue,
                count=finding.count,
                severity=finding.severity,
                description=finding.description,
            )
        )

    # Normalize invalid-value findings
    for finding in invalid_findings:
        all_findings.append(
            AtlasFinding(
                category="data_quality",
                column=finding.column,
                issue=finding.issue,
                count=finding.count,
                severity=finding.severity,
                description=finding.description,
            )
        )

    # Normalize PII findings
    for finding in pii_findings:
        all_findings.append(
            AtlasFinding(
                category="governance",
                column=finding.column,
                issue="pii_detected",
                count=1,
                severity="high",
                description=finding.reason,
            )
        )

    # Normalize behavioral anomaly findings
    for finding in anomaly_findings:
        all_findings.append(
            AtlasFinding(
                category="behavioral_anomaly",
                column=finding.column,
                issue=finding.issue,
                count=finding.count,
                severity=finding.severity,
                description=finding.description,
            )
        )

    return {
        "quality_findings": quality_findings,
        "duplicate_findings": duplicate_findings,
        "invalid_findings": invalid_findings,
        "pii_findings": pii_findings,
        "anomaly_findings": anomaly_findings,
        "all_findings": all_findings,
    }