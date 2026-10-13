import pandas as pd

from app.governance.evidence import collect_finding_evidence
from app.governance.pii import detect_pii_columns
from app.governance.sanitizer import sanitize_evidence
from app.models.metadata import AtlasFinding


def test_detect_pii_columns():

    df = pd.DataFrame(
        {
            "customer_id": [1001],
            "customer_name": ["Ava Johnson"],
            "email": ["ava@example.com"],
            "phone": ["2145550101"],
            "date_of_birth": ["1998-04-12"],
            "country": ["USA"],
            "account_type": ["Premium"],
            "annual_spend": [12500.50],
        }
    )

    findings = detect_pii_columns(df)

    pii_columns = [
        finding.column
        for finding in findings
    ]

    assert "email" in pii_columns
    assert "phone" in pii_columns
    assert "date_of_birth" in pii_columns

    assert len(findings) == 3


def test_sanitize_pii_evidence():

    df = pd.DataFrame(
        {
            "customer_id": [1001],
            "customer_name": ["Ava Johnson"],
            "email": ["ava@example.com"],
            "phone": ["2145550101"],
            "date_of_birth": ["1998-04-12"],
            "country": ["USA"],
            "account_type": ["Premium"],
            "annual_spend": [12500.50],
        }
    )

    finding = AtlasFinding(
        category="governance",
        column="email",
        issue="pii_detected",
        count=1,
        severity="high",
        description=(
            "Column 'email' may contain "
            "personally identifiable information."
        ),
    )

    evidence = collect_finding_evidence(
        df=df,
        finding=finding,
    )

    sanitized = sanitize_evidence(
        evidence=evidence,
        finding=finding,
    )

    assert len(sanitized) == 1

    row_data = sanitized[0]["row_data"]

    assert row_data["email"] == "[REDACTED]"
    assert row_data["phone"] == "[REDACTED]"
    assert row_data["date_of_birth"] == "[REDACTED]"

    assert row_data["customer_id"] == 1001
    assert row_data["customer_name"] == "Ava Johnson"
    assert row_data["country"] == "USA"
    assert row_data["account_type"] == "Premium"
    assert row_data["annual_spend"] == 12500.50


def test_sanitized_evidence_does_not_expose_pii():

    df = pd.DataFrame(
        {
            "customer_id": [1001],
            "customer_name": ["Ava Johnson"],
            "email": ["ava@example.com"],
            "phone": ["2145550101"],
            "date_of_birth": ["1998-04-12"],
            "country": ["USA"],
            "account_type": ["Premium"],
            "annual_spend": [12500.50],
        }
    )

    finding = AtlasFinding(
        category="governance",
        column="email",
        issue="pii_detected",
        count=1,
        severity="high",
        description=(
            "Column 'email' may contain "
            "personally identifiable information."
        ),
    )

    evidence = collect_finding_evidence(
        df=df,
        finding=finding,
    )

    sanitized = sanitize_evidence(
        evidence=evidence,
        finding=finding,
    )

    serialized_evidence = str(sanitized)

    assert "ava@example.com" not in serialized_evidence
    assert "2145550101" not in serialized_evidence
    assert "1998-04-12" not in serialized_evidence

    assert "[REDACTED]" in serialized_evidence