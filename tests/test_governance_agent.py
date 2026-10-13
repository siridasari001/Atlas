from dotenv import load_dotenv
import pandas as pd
import pytest

load_dotenv()

from app.agents.context_builder import GovernanceContextBuilder
from app.agents.governance_agent import GovernanceAgent
from app.llm.client import LLMClient
from app.models.metadata import AtlasFinding
from app.retrieval.retriever import KnowledgeRetriever
from app.retrieval.vector_store import KnowledgeVectorStore


def get_agent():

    vector_store = KnowledgeVectorStore()

    retriever = KnowledgeRetriever(
        vector_store
    )

    context_builder = GovernanceContextBuilder(
        retriever
    )

    llm_client = LLMClient()

    return GovernanceAgent(
        context_builder=context_builder,
        llm_client=llm_client,
    )


def test_governance_agent_explains_negative_annual_spend(
    run_live_llm,
):

    if not run_live_llm:
        pytest.skip(
            "Live LLM test. Run with --run-live-llm."
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

    df = pd.DataFrame(
        {
            "customer_id": [1007],
            "customer_name": ["Sophia Moore"],
            "email": ["sophia@example.com"],
            "phone": ["2145550107"],
            "date_of_birth": ["1999-07-30"],
            "country": ["USA"],
            "account_type": ["Standard"],
            "annual_spend": [-500.00],
        }
    )

    agent = get_agent()

    response = agent.explain_finding(
        df=df,
        finding=finding,
        user_question="Why was annual_spend flagged?",
    )

    assert isinstance(response, str)
    assert len(response.strip()) > 0

    response_text = response.lower()

    assert "annual_spend" in response_text
    assert "negative" in response_text


def test_governance_agent_explains_missing_email(
    run_live_llm,
):

    if not run_live_llm:
        pytest.skip(
            "Live LLM test. Run with --run-live-llm."
        )

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

    df = pd.DataFrame(
        {
            "customer_id": [1003],
            "customer_name": ["Olivia Brown"],
            "email": [None],
            "phone": ["2145550103"],
            "date_of_birth": ["2001-11-03"],
            "country": ["USA"],
            "account_type": ["Standard"],
            "annual_spend": [3100.75],
        }
    )

    agent = get_agent()

    response = agent.explain_finding(
        df=df,
        finding=finding,
        user_question=(
            "Why is the email column incomplete?"
        ),
    )

    assert isinstance(response, str)
    assert len(response.strip()) > 0

    response_text = response.lower()

    assert "email" in response_text
    assert "missing" in response_text


def test_governance_agent_protects_pii(
    run_live_llm,
):

    if not run_live_llm:
        pytest.skip(
            "Live LLM test. Run with --run-live-llm."
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

    agent = get_agent()

    response = agent.explain_finding(
        df=df,
        finding=finding,
        user_question="Why is email considered PII?",
    )

    assert isinstance(response, str)
    assert len(response.strip()) > 0

    assert "ava@example.com" not in response
    assert "2145550101" not in response
    assert "1998-04-12" not in response

    response_text = response.lower()

    assert "pii" in response_text