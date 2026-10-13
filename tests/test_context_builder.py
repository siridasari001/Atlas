import pandas as pd

from app.agents.context_builder import GovernanceContextBuilder
from app.models.metadata import AtlasFinding
from app.retrieval.retriever import KnowledgeRetriever
from app.retrieval.vector_store import KnowledgeVectorStore


def get_context_builder():

    vector_store = KnowledgeVectorStore()

    retriever = KnowledgeRetriever(
        vector_store
    )

    return GovernanceContextBuilder(
        retriever
    )


def get_customer_dataframe():

    return pd.DataFrame(
        {
            "customer_id": [1001, 1002],
            "customer_name": [
                "Ava Johnson",
                "Liam Smith",
            ],
            "email": [
                "ava@example.com",
                None,
            ],
            "phone": [
                "2145550101",
                "2145550102",
            ],
            "date_of_birth": [
                "1998-04-12",
                "1995-08-21",
            ],
            "country": [
                "USA",
                "USA",
            ],
            "account_type": [
                "Premium",
                "Standard",
            ],
            "annual_spend": [
                12500.50,
                4200.00,
            ],
        }
    )


def test_context_builder_collects_governance_and_remediation():

    df = get_customer_dataframe()

    finding = AtlasFinding(
        category="data_quality",
        column="email",
        issue="missing_values",
        count=1,
        severity="medium",
        description=(
            "Column 'email' contains missing values."
        ),
    )

    context_builder = get_context_builder()

    context = context_builder.build_context(
        df=df,
        finding=finding.model_dump(),
        query="Why is email missing?",
        top_k=3,
    )

    assert context["finding"]["issue"] == "missing_values"

    assert len(context["evidence"]) == 1

    assert context["evidence"][0]["column"] == "email"

    assert context["evidence"][0]["value"] == "[REDACTED]"

    assert len(context["retrieved_knowledge"]) > 0

    categories = [
        item["category"]
        for item in context["retrieved_knowledge"]
    ]

    assert "data_quality" in categories
    assert "remediation" in categories


def test_context_builder_redacts_pii():

    df = get_customer_dataframe()

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

    context_builder = get_context_builder()

    context = context_builder.build_context(
        df=df,
        finding=finding.model_dump(),
        query="Why is email considered PII?",
        top_k=3,
    )

    evidence = context["evidence"]

    assert len(evidence) == 1

    row_data = evidence[0]["row_data"]

    assert row_data["email"] == "[REDACTED]"

    assert "ava@example.com" not in str(evidence)

    assert "PII" in str(
        context["retrieved_knowledge"]
    )


def test_context_builder_handles_negative_spend():

    df = pd.DataFrame(
        {
            "customer_id": [1001],
            "customer_name": ["Ava Johnson"],
            "email": ["ava@example.com"],
            "phone": ["2145550101"],
            "date_of_birth": ["1998-04-12"],
            "country": ["USA"],
            "account_type": ["Premium"],
            "annual_spend": [-500.00],
        }
    )

    finding = AtlasFinding(
        category="data_quality",
        column="annual_spend",
        issue="invalid_negative_value",
        count=1,
        severity="high",
        description=(
            "Annual spend cannot contain negative values."
        ),
    )

    context_builder = get_context_builder()

    context = context_builder.build_context(
        df=df,
        finding=finding.model_dump(),
        query="Why was annual_spend flagged?",
        top_k=3,
    )

    assert len(context["evidence"]) == 1

    assert context["evidence"][0]["value"] == -500.00

    knowledge_text = str(
        context["retrieved_knowledge"]
    )

    assert "Annual Spend" in knowledge_text
    assert "Negative Annual Spend" in knowledge_text