import pandas as pd

from app.governance.analyzer import analyze_dataset


def test_analyze_dataset_detects_expected_findings():

    data = {
        "customer_id": [
            1001,
            1002,
            1003,
            1004,
            1005,
            1006,
            1007,
            1008,
            1009,
            1010,
            1010,
            1011,
            1012,
        ],
        "customer_name": [
            "Ava Johnson",
            "Liam Smith",
            "Olivia Brown",
            "Noah Davis",
            "Emma Wilson",
            "James Miller",
            "Sophia Moore",
            "William Taylor",
            "Isabella Anderson",
            "Benjamin Thomas",
            "Benjamin Thomas",
            "Mia Jackson",
            "Lucas White",
        ],
        "email": [
            "ava.johnson@email.com",
            "liam.smith@email.com",
            None,
            "noah.davis@email.com",
            "emma.wilson@email.com",
            "james.miller@email.com",
            "sophia.moore@email.com",
            "william.taylor@email.com",
            "isabella.anderson@email.com",
            "benjamin.thomas@email.com",
            "benjamin.thomas@email.com",
            "mia.jackson@email.com",
            "lucas.white@email.com",
        ],
        "phone": [
            "2145550101",
            "2145550102",
            "2145550103",
            None,
            "2145550105",
            "2145550106",
            "2145550107",
            "2145550108",
            "2145550109",
            "2145550110",
            "2145550110",
            "2145550112",
            "2145550113",
        ],
        "date_of_birth": [
            "1998-04-12",
            "1995-08-21",
            "2001-11-03",
            "1992-06-18",
            None,
            "1988-02-14",
            "1999-07-30",
            "1990-10-09",
            "2002-01-25",
            "1985-05-17",
            "1985-05-17",
            "1997-09-11",
            "1993-12-02",
        ],
        "country": [
            "USA",
            "USA",
            "USA",
            "Canada",
            "USA",
            "USA",
            "USA",
            "USA",
            "USA",
            "USA",
            "USA",
            "USA",
            "USA",
        ],
        "account_type": [
            "Premium",
            "Standard",
            "Standard",
            "Premium",
            "Basic",
            "Premium",
            "Standard",
            "Premium",
            "Basic",
            "Standard",
            "Standard",
            "Premium",
            "Standard",
        ],
        "annual_spend": [
            12500.50,
            4200.00,
            3100.75,
            18900.00,
            850.25,
            22100.40,
            -500.00,
            15750.00,
            1200.00,
            5600.50,
            5600.50,
            13200.00,
            4700.25,
        ],
    }

    df = pd.DataFrame(data)

    analysis = analyze_dataset(df)

    findings = analysis["all_findings"]

    assert len(findings) == 8

    issues = [
        finding.issue
        for finding in findings
    ]

    assert issues.count("missing_values") == 3
    assert issues.count("duplicate_records") == 1
    assert issues.count("invalid_negative_value") == 1
    assert issues.count("pii_detected") == 3


def test_duplicate_record_finding():

    data = {
        "customer_id": [1001, 1002, 1002],
        "customer_name": [
            "Ava Johnson",
            "Liam Smith",
            "Liam Smith",
        ],
        "email": [
            "ava@email.com",
            "liam@email.com",
            "liam@email.com",
        ],
        "phone": [
            "1111111111",
            "2222222222",
            "2222222222",
        ],
        "date_of_birth": [
            "1998-01-01",
            "1995-01-01",
            "1995-01-01",
        ],
        "country": [
            "USA",
            "USA",
            "USA",
        ],
        "account_type": [
            "Premium",
            "Standard",
            "Standard",
        ],
        "annual_spend": [
            1000.00,
            2000.00,
            2000.00,
        ],
    }

    df = pd.DataFrame(data)

    analysis = analyze_dataset(df)

    duplicate_findings = analysis[
        "duplicate_findings"
    ]

    assert len(duplicate_findings) == 1

    assert (
        duplicate_findings[0].issue
        == "duplicate_records"
    )

    assert (
        duplicate_findings[0].count
        == 1
    )


def test_negative_annual_spend_finding():

    data = {
        "customer_id": [1001],
        "customer_name": ["Ava Johnson"],
        "email": ["ava@email.com"],
        "phone": ["1111111111"],
        "date_of_birth": ["1998-01-01"],
        "country": ["USA"],
        "account_type": ["Premium"],
        "annual_spend": [-500.00],
    }

    df = pd.DataFrame(data)

    analysis = analyze_dataset(df)

    invalid_findings = analysis[
        "invalid_findings"
    ]

    assert len(invalid_findings) == 1

    assert (
        invalid_findings[0].issue
        == "invalid_negative_value"
    )

    assert (
        invalid_findings[0].column
        == "annual_spend"
    )

    assert (
        invalid_findings[0].count
        == 1
    )