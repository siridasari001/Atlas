import pandas as pd

from app.governance.anomalies import detect_numeric_anomalies
from app.governance.evidence import collect_finding_evidence
from app.models.metadata import AtlasFinding


def test_detects_behavioral_anomaly():
    df = pd.DataFrame(
        {
            "annual_spend": [
                850.25,
                1200.00,
                3100.75,
                4200.00,
                4700.25,
                5600.50,
                12500.50,
                13200.00,
                15750.00,
                18900.00,
                22100.40,
                -500.00,
                125000.00,
            ]
        }
    )

    findings = detect_numeric_anomalies(df)

    assert len(findings) == 1

    finding = findings[0]

    assert finding.column == "annual_spend"
    assert finding.issue == "behavioral_anomaly"
    assert finding.count == 1
    assert finding.severity == "medium"


def test_does_not_flag_normal_values_as_anomalies():
    df = pd.DataFrame(
        {
            "annual_spend": [
                1000.00,
                1200.00,
                1500.00,
                1800.00,
                2000.00,
                2200.00,
                2500.00,
                2800.00,
            ]
        }
    )

    findings = detect_numeric_anomalies(df)

    assert findings == []


def test_skips_very_small_datasets():
    df = pd.DataFrame(
        {
            "annual_spend": [
                1000.00,
                2000.00,
                3000.00,
                100000.00,
            ]
        }
    )

    findings = detect_numeric_anomalies(df)

    assert findings == []


def test_collects_behavioral_anomaly_evidence():
    df = pd.DataFrame(
        {
            "customer_id": [1001, 1002, 1003, 1004, 1005, 1006],
            "annual_spend": [
                1000.00,
                1200.00,
                1500.00,
                1800.00,
                2000.00,
                100000.00,
            ],
        }
    )

    finding = AtlasFinding(
        category="behavioral_anomaly",
        column="annual_spend",
        issue="behavioral_anomaly",
        count=1,
        severity="medium",
        description="Statistical anomaly detected.",
    )

    evidence = collect_finding_evidence(
        df=df,
        finding=finding,
    )

    assert len(evidence) == 1
    assert evidence[0]["row_index"] == 5
    assert evidence[0]["column"] == "annual_spend"
    assert evidence[0]["value"] == 100000.00