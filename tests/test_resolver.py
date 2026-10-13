from app.governance.analyzer import analyze_dataset
from app.governance.resolver import FindingResolver
from app.ingestion.loader import load_csv


def get_findings():

    df = load_csv(
        "data/raw/customers.csv"
    )

    analysis = analyze_dataset(df)

    return analysis["all_findings"]


def test_resolve_annual_spend_question():

    findings = get_findings()

    resolver = FindingResolver()

    finding = resolver.resolve(
        question="Why was annual_spend flagged?",
        findings=findings,
    )

    assert finding is not None

    assert finding.issue == "invalid_negative_value"

    assert finding.column == "annual_spend"


def test_resolve_email_pii_question():

    findings = get_findings()

    resolver = FindingResolver()

    finding = resolver.resolve(
        question="Why is email considered PII?",
        findings=findings,
    )

    assert finding is not None

    assert finding.issue == "pii_detected"

    assert finding.column == "email"


def test_resolve_missing_phone_question():

    findings = get_findings()

    resolver = FindingResolver()

    finding = resolver.resolve(
        question="Why is the phone column incomplete?",
        findings=findings,
    )

    assert finding is not None

    assert finding.issue == "missing_values"

    assert finding.column == "phone"


def test_resolve_duplicate_question():

    findings = get_findings()

    resolver = FindingResolver()

    finding = resolver.resolve(
        question="Why are there duplicate records?",
        findings=findings,
    )

    assert finding is not None

    assert finding.issue == "duplicate_records"

    assert finding.column is None