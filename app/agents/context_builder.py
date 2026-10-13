import pandas as pd

from app.governance.evidence import collect_finding_evidence
from app.governance.sanitizer import sanitize_evidence
from app.models.metadata import AtlasFinding
from app.retrieval.retriever import KnowledgeRetriever


class GovernanceContextBuilder:
    """
    Combine deterministic Atlas findings, sanitized dataset evidence,
    governance knowledge, and remediation knowledge.
    """

    def __init__(self, retriever: KnowledgeRetriever):
        self.retriever = retriever

    def build_context(
        self,
        df: pd.DataFrame,
        finding: dict,
        query: str,
        top_k: int = 3,
    ) -> dict:

        atlas_finding = AtlasFinding(**finding)

        # --------------------------------------------------
        # 1. Collect concrete evidence from the dataset
        # --------------------------------------------------

        evidence = collect_finding_evidence(
            df=df,
            finding=atlas_finding,
        )

        # --------------------------------------------------
        # 2. Sanitize evidence before downstream use
        # --------------------------------------------------

        sanitized_evidence = sanitize_evidence(
            evidence=evidence,
            finding=atlas_finding,
        )

        # --------------------------------------------------
        # 3. Determine the governance knowledge category
        # --------------------------------------------------

        governance_category = "governance"

        if atlas_finding.category == "data_quality":
            governance_category = "data_quality"

        elif atlas_finding.category == "data_integrity":
            governance_category = "data_integrity"

        elif atlas_finding.issue == "pii_detected":
            governance_category = "pii"

        # --------------------------------------------------
        # 4. Retrieve applicable governance knowledge
        # --------------------------------------------------

        governance_knowledge = self.retriever.search(
            query=query,
            top_k=top_k,
            category=governance_category,
        )

        # --------------------------------------------------
        # 5. Retrieve remediation knowledge
        # --------------------------------------------------

        remediation_query = (
            f"What approved remediation guidance applies to "
            f"the {atlas_finding.issue} issue in the "
            f"{atlas_finding.column} column?"
        )

        remediation_knowledge = self.retriever.search(
            query=remediation_query,
            top_k=top_k,
            category="remediation",
        )

        # --------------------------------------------------
        # 6. Combine knowledge for the reasoning layer
        # --------------------------------------------------

        retrieved_knowledge = (
            governance_knowledge
            + remediation_knowledge
        )

        return {
            "finding": finding,
            "evidence": sanitized_evidence,
            "retrieved_knowledge": retrieved_knowledge,
        }