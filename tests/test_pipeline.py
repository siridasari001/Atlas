from dotenv import load_dotenv
import pandas as pd
import pytest

load_dotenv()

from app.agents.context_builder import GovernanceContextBuilder
from app.agents.governance_agent import GovernanceAgent
from app.governance.analyzer import analyze_dataset
from app.governance.resolver import FindingResolver
from app.llm.client import LLMClient
from app.retrieval.retriever import KnowledgeRetriever
from app.retrieval.vector_store import KnowledgeVectorStore


def build_atlas():

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


def test_full_atlas_pipeline(run_live_llm):

    if not run_live_llm:
        pytest.skip(
            "Live LLM test. Run with --run-live-llm."
        )

    df = pd.read_csv(
        "data/raw/customers.csv"
    )

    analysis = analyze_dataset(df)

    findings = analysis["all_findings"]

    assert len(findings) == 8

    resolver = FindingResolver()

    question = "Why was annual_spend flagged?"

    finding = resolver.resolve(
        question=question,
        findings=findings,
    )

    assert finding is not None
    assert finding.issue == "invalid_negative_value"
    assert finding.column == "annual_spend"

    agent = build_atlas()

    response = agent.explain_finding(
        df=df,
        finding=finding,
        user_question=question,
    )

    assert isinstance(response, str)
    assert len(response.strip()) > 0

    response_text = response.lower()

    assert "annual_spend" in response_text
    assert "negative" in response_text


def test_full_atlas_pipeline_protects_pii(
    run_live_llm,
):

    if not run_live_llm:
        pytest.skip(
            "Live LLM test. Run with --run-live-llm."
        )

    df = pd.read_csv(
        "data/raw/customers.csv"
    )

    analysis = analyze_dataset(df)

    findings = analysis["all_findings"]

    resolver = FindingResolver()

    question = "Why is email considered PII?"

    finding = resolver.resolve(
        question=question,
        findings=findings,
    )

    assert finding is not None
    assert finding.issue == "pii_detected"
    assert finding.column == "email"

    agent = build_atlas()

    response = agent.explain_finding(
        df=df,
        finding=finding,
        user_question=question,
    )

    assert isinstance(response, str)
    assert len(response.strip()) > 0

    assert "ava.johnson@email.com" not in response
    assert "2145550101" not in response
    assert "1998-04-12" not in response

    response_text = response.lower()

    assert "pii" in response_text


def test_full_atlas_pipeline_handles_duplicate_records(
    run_live_llm,
):

    if not run_live_llm:
        pytest.skip(
            "Live LLM test. Run with --run-live-llm."
        )

    df = pd.read_csv(
        "data/raw/customers.csv"
    )

    analysis = analyze_dataset(df)

    findings = analysis["all_findings"]

    resolver = FindingResolver()

    question = "Why are there duplicate records?"

    finding = resolver.resolve(
        question=question,
        findings=findings,
    )

    assert finding is not None
    assert finding.issue == "duplicate_records"

    agent = build_atlas()

    response = agent.explain_finding(
        df=df,
        finding=finding,
        user_question=question,
    )

    assert isinstance(response, str)
    assert len(response.strip()) > 0

    response_text = response.lower()

    assert "duplicate" in response_text