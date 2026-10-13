from app.agents.context_builder import GovernanceContextBuilder
from app.llm.client import LLMClient
from app.llm.prompts import build_governance_prompt
from app.models.metadata import AtlasFinding


class GovernanceAgent:
    """
    Orchestrate Atlas governance reasoning.

    The agent combines deterministic findings, sanitized dataset
    evidence, retrieved governance knowledge, and the LLM to
    produce a grounded explanation.
    """

    def __init__(
        self,
        context_builder: GovernanceContextBuilder,
        llm_client: LLMClient,
    ):
        self.context_builder = context_builder
        self.llm_client = llm_client

    def explain_finding(
        self,
        df,
        finding: AtlasFinding,
        user_question: str,
        top_k: int = 3,
    ) -> str:
        """
        Explain an Atlas finding using the dataset evidence,
        retrieved governance knowledge, and the LLM.
        """

        finding_data = {
            "category": finding.category,
            "column": finding.column,
            "issue": finding.issue,
            "count": finding.count,
            "severity": finding.severity,
            "description": finding.description,
        }

        context = self.context_builder.build_context(
            df=df,
            finding=finding_data,
            query=user_question,
            top_k=top_k,
        )

        prompt = build_governance_prompt(
            finding=context["finding"],
            evidence=context["evidence"],
            retrieved_knowledge=context["retrieved_knowledge"],
            user_question=user_question,
        )

        return self.llm_client.generate(prompt)