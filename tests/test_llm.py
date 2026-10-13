from dotenv import load_dotenv
import pytest

load_dotenv()

from app.llm.client import LLMClient
from app.llm.prompts import build_governance_prompt


def test_governance_prompt_contains_grounded_context():

    finding = {
        "category": "data_quality",
        "column": "annual_spend",
        "issue": "invalid_negative_value",
        "count": 1,
        "severity": "high",
        "description": (
            "Annual spend cannot contain negative values."
        ),
    }

    evidence = [
        {
            "row_index": 6,
            "column": "annual_spend",
            "value": -500.00,
            "row_data": {
                "customer_id": 1007,
                "customer_name": "Sophia Moore",
                "email": "[REDACTED]",
                "phone": "[REDACTED]",
                "date_of_birth": "[REDACTED]",
                "country": "USA",
                "account_type": "Standard",
                "annual_spend": -500.00,
            },
        }
    ]

    retrieved_knowledge = [
        {
            "content": (
                "The `annual_spend` column represents the amount "
                "a customer has spent. Annual spend must not "
                "contain negative values."
            ),
            "source": "data/knowledge/governance_rules.md",
            "category": "data_quality",
            "chunk_id": 5,
            "distance": 0.5,
        },
        {
            "content": (
                "The `annual_spend` column must contain "
                "non-negative values. Verify the value against "
                "the upstream source system and confirm with "
                "the data owner."
            ),
            "source": "data/knowledge/remediation_rules.md",
            "category": "remediation",
            "chunk_id": 1,
            "distance": 0.7,
        },
    ]

    prompt = build_governance_prompt(
        finding=finding,
        evidence=evidence,
        retrieved_knowledge=retrieved_knowledge,
        user_question="Why was annual_spend flagged?",
    )

    assert "annual_spend" in prompt
    assert "invalid_negative_value" in prompt
    assert "-500.0" in prompt
    assert "Annual spend must not contain negative values" in prompt
    assert "data owner" in prompt
    assert "[REDACTED]" in prompt


def test_governance_prompt_protects_redacted_pii():

    finding = {
        "category": "governance",
        "column": "email",
        "issue": "pii_detected",
        "count": 1,
        "severity": "high",
        "description": (
            "Column 'email' may contain "
            "personally identifiable information."
        ),
    }

    evidence = [
        {
            "row_index": 0,
            "column": "email",
            "value": "[REDACTED]",
            "row_data": {
                "customer_id": 1001,
                "customer_name": "Ava Johnson",
                "email": "[REDACTED]",
                "phone": "[REDACTED]",
                "date_of_birth": "[REDACTED]",
                "country": "USA",
                "account_type": "Premium",
                "annual_spend": 12500.50,
            },
        }
    ]

    retrieved_knowledge = [
        {
            "content": (
                "The `email` column contains personally "
                "identifiable information (PII)."
            ),
            "source": "data/knowledge/governance_rules.md",
            "category": "pii",
            "chunk_id": 1,
            "distance": 0.5,
        },
        {
            "content": (
                "Columns classified as PII should be protected "
                "from unnecessary exposure."
            ),
            "source": "data/knowledge/remediation_rules.md",
            "category": "remediation",
            "chunk_id": 4,
            "distance": 0.7,
        },
    ]

    prompt = build_governance_prompt(
        finding=finding,
        evidence=evidence,
        retrieved_knowledge=retrieved_knowledge,
        user_question="Why is email considered PII?",
    )

    assert "PII" in prompt
    assert "[REDACTED]" in prompt

    assert "ava@example.com" not in prompt
    assert "2145550101" not in prompt
    assert "1998-04-12" not in prompt


def test_llm_generates_grounded_response(run_live_llm):

    if not run_live_llm:
        pytest.skip(
            "Live LLM test. Run with --run-live-llm."
        )

    client = LLMClient()

    prompt = """
You are testing the Atlas governance reasoning layer.

Use ONLY the information below.

Finding:
Column: annual_spend
Issue: invalid_negative_value
Count: 1
Severity: high
Description: Annual spend cannot contain negative values.

Evidence:
Row index: 6
annual_spend: -500.0

Governance knowledge:
Annual spend must not contain negative values.

Remediation knowledge:
Verify the value against the upstream source system.
Confirm with the data owner.
If invalid, correct it using the approved source-system value.

Question:
Why was annual_spend flagged?

Give a concise explanation.
""".strip()

    response = client.generate(prompt)

    assert isinstance(response, str)
    assert len(response.strip()) > 0

    response_text = response.lower()

    assert "annual_spend" in response_text
    assert "negative" in response_text