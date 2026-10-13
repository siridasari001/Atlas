from dotenv import load_dotenv
import pytest

load_dotenv()

from app.agents.context_builder import GovernanceContextBuilder
from app.agents.governance_agent import GovernanceAgent
from app.governance.analyzer import analyze_dataset
from app.governance.resolver import FindingResolver
from app.ingestion.loader import load_csv
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


def test_multiple_questions_resolve_to_correct_findings():

    df = load_csv(
        "data/raw/customers.csv"
    )

    analysis = analyze_dataset(df)

    findings = analysis["all_findings"]

    resolver = FindingResolver()

    questions_and_expected = [
        (
            "Why was annual_spend flagged?",
            "invalid_negative_value",
            "annual_spend",
        ),
        (
            "Why is email considered PII?",
            "pii_detected",
            "email",
        ),
        (
            "Why is the phone column incomplete?",
            "missing_values",
            "phone",
        ),
        (
            "Why are there duplicate records?",
            "duplicate_records",
            None,
        ),
    ]

    for (
        question,
        expected_issue,
        expected_column,
    ) in questions_and_expected:

        finding = resolver.resolve(
            question=question,
            findings=findings,
        )

        assert finding is not None
        assert finding.issue == expected_issue
        assert finding.column == expected_column


def test_multiple_questions_generate_grounded_responses(
    run_live_llm,
):

    if not run_live_llm:
        pytest.skip(
            "Live LLM test. Run with --run-live-llm."
        )

    df = load_csv(
        "data/raw/customers.csv"
    )

    analysis = analyze_dataset(df)

    findings = analysis["all_findings"]

    resolver = FindingResolver()

    atlas = build_atlas()

    questions = [
        "Why was annual_spend flagged?",
        "Why is email considered PII?",
        "Why is the phone column incomplete?",
        "Why are there duplicate records?",
    ]

    for question in questions:

        finding = resolver.resolve(
            question=question,
            findings=findings,
        )

        assert finding is not None

        response = atlas.explain_finding(
            df=df,
            finding=finding,
            user_question=question,
        )

        assert isinstance(response, str)
        assert len(response.strip()) > 0


def test_multiple_questions_do_not_expose_pii(
    run_live_llm,
):

    if not run_live_llm:
        pytest.skip(
            "Live LLM test. Run with --run-live-llm."
        )

    df = load_csv(
        "data/raw/customers.csv"
    )

    analysis = analyze_dataset(df)

    findings = analysis["all_findings"]

    resolver = FindingResolver()

    atlas = build_atlas()

    questions = [
        "Why is email considered PII?",
        "Why is the phone column incomplete?",
        "Why are there duplicate records?",
    ]

    sensitive_values = [
        "ava.johnson@email.com",
        "2145550101",
        "1998-04-12",
    ]

    for question in questions:

        finding = resolver.resolve(
            question=question,
            findings=findings,
        )

        assert finding is not None

        response = atlas.explain_finding(
            df=df,
            finding=finding,
            user_question=question,
        )

        for sensitive_value in sensitive_values:
            assert sensitive_value not in response