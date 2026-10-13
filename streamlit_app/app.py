import sys
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv


# ============================================================
# Project path
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# Environment
# ============================================================

load_dotenv()


# ============================================================
# Atlas imports
# ============================================================

from app.agents.context_builder import GovernanceContextBuilder
from app.agents.governance_agent import GovernanceAgent

from app.governance.analyzer import analyze_dataset
from app.governance.evidence import collect_finding_evidence
from app.governance.resolver import FindingResolver
from app.governance.sanitizer import sanitize_evidence

from app.llm.client import LLMClient

from app.models.metadata import PII_COLUMNS

from app.reporting.report_generator import generate_governance_report

from app.retrieval.retriever import KnowledgeRetriever
from app.retrieval.vector_store import KnowledgeVectorStore


# ============================================================
# Page configuration
# ============================================================

st.set_page_config(
    page_title="Atlas | Data Intelligence & Governance",
    page_icon="🔎",
    layout="wide",
)


# ============================================================
# Custom styling
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 2.5rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    .atlas-badge {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 999px;
        background: #eef2ff;
        color: #4f46e5;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.7px;
        text-transform: uppercase;
        margin-bottom: 12px;
    }

    .atlas-footer {
        margin-top: 45px;
        padding-top: 20px;
        border-top: 1px solid #e5e7eb;
        color: #94a3b8;
        font-size: 12px;
        line-height: 1.8;
    }

    .severity-high {
        padding: 8px 12px;
        border-radius: 8px;
        background: #fef2f2;
        color: #b91c1c;
        font-weight: 700;
        display: inline-block;
    }

    .severity-medium {
        padding: 8px 12px;
        border-radius: 8px;
        background: #fffbeb;
        color: #a16207;
        font-weight: 700;
        display: inline-block;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Atlas components
# ============================================================

@st.cache_resource
def create_atlas_components():
    """
    Create and cache the core Atlas components.

    Returns:
        A tuple containing the GovernanceAgent and
        GovernanceContextBuilder.
    """

    vector_store = KnowledgeVectorStore()

    retriever = KnowledgeRetriever(
        vector_store
    )

    context_builder = GovernanceContextBuilder(
        retriever
    )

    llm_client = LLMClient()

    agent = GovernanceAgent(
        context_builder=context_builder,
        llm_client=llm_client,
    )

    return agent, context_builder


# ============================================================
# Privacy-safe preview
# ============================================================

def create_privacy_safe_preview(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create a privacy-safe copy of a dataset.

    All columns classified as PII are replaced with
    [REDACTED] before being displayed.
    """

    preview_df = df.copy()

    for column in preview_df.columns:

        if column.lower() in PII_COLUMNS:
            preview_df[column] = "[REDACTED]"

    return preview_df


# ============================================================
# Finding label
# ============================================================

def finding_label(finding) -> str:
    """
    Create a human-readable label for a finding.
    """

    column = (
        finding.column
        if finding.column is not None
        else "Dataset-level"
    )

    return (
        f"{finding.issue} | "
        f"{column} | "
        f"{finding.severity.upper()}"
    )


# ============================================================
# Governance query builder
# ============================================================

def build_governance_query(finding) -> str:
    """
    Build a targeted retrieval query for the governance
    knowledge base.

    The query is intentionally specific so that findings such
    as duplicate records retrieve the correct governance rule
    instead of an unrelated policy.
    """

    if finding.issue == "duplicate_records":

        return (
            "Customer ID uniqueness, duplicate customer records, "
            "data integrity, and duplicate record governance policy"
        )

    if finding.issue == "invalid_negative_value":

        return (
            f"Governance policy for invalid negative values "
            f"in {finding.column}"
        )

    if finding.issue == "missing_values":

        return (
            f"Governance policy for missing values "
            f"in {finding.column}"
        )

    if finding.issue == "pii_detected":

        return (
            f"PII governance policy for the "
            f"{finding.column} column and protection of "
            f"personally identifiable information"
        )

    return (
        f"Governance policy for "
        f"{finding.issue} "
        f"{finding.column or 'dataset'}"
    )


# ============================================================
# Header
# ============================================================

st.markdown(
    '<div class="atlas-badge">Enterprise Data Intelligence</div>',
    unsafe_allow_html=True,
)

st.title("🔎 Atlas")

st.subheader(
    "Data Intelligence & Governance Copilot"
)

st.write(
    "Detect data-quality issues, investigate governance risks, "
    "retrieve approved policies, and generate grounded explanations "
    "using enterprise knowledge."
)


# ============================================================
# Privacy banner
# ============================================================

with st.container(border=True):

    st.markdown(
        "### 🔐 Privacy-Safe by Design"
    )

    st.write(
        "PII is automatically redacted from dataset previews, "
        "evidence, and downstream AI context."
    )


# ============================================================
# How Atlas Works
# ============================================================

st.header("How Atlas Works")

st.write(
    "Atlas combines deterministic data-quality checks, "
    "governance rules, retrieval-augmented generation, "
    "and grounded LLM reasoning."
)


architecture_columns = st.columns(4)


architecture_cards = [
    (
        "🔎",
        "1. Detect",
        "Deterministic Python rules identify missing values, "
        "duplicates, invalid values, and PII.",
    ),
    (
        "🛡️",
        "2. Govern",
        "Atlas maps findings to approved governance policies "
        "and data-quality rules.",
    ),
    (
        "📚",
        "3. Retrieve",
        "ChromaDB retrieves relevant governance and remediation "
        "knowledge using semantic search.",
    ),
    (
        "🤖",
        "4. Explain",
        "The LLM generates grounded explanations using "
        "deterministic findings, sanitized evidence, and "
        "approved knowledge.",
    ),
]


for column, card in zip(
    architecture_columns,
    architecture_cards,
):

    icon, title, description = card

    with column:

        with st.container(border=True):

            st.markdown(
                f"### {icon}"
            )

            st.markdown(
                f"**{title}**"
            )

            st.caption(
                description
            )


# ============================================================
# Divider
# ============================================================

st.divider()


# ============================================================
# Sidebar
# ============================================================

with st.sidebar:

    st.header("Atlas")

    st.write(
        "Upload a dataset and use natural language "
        "to investigate governance findings."
    )

    st.divider()

    st.caption("Atlas Environment")

    st.success("Development")

    st.divider()

    st.caption("Privacy")

    st.write(
        "PII is automatically redacted from "
        "dataset previews, evidence, and downstream AI context."
    )


# ============================================================
# Dataset
# ============================================================

st.header("Dataset")


uploaded_file = st.file_uploader(
    "Upload a CSV dataset",
    type=["csv"],
)


# ============================================================
# No dataset uploaded
# ============================================================

if uploaded_file is None:

    st.info(
        "Upload a CSV file to begin analyzing your dataset."
    )


# ============================================================
# Dataset uploaded
# ============================================================

else:

    # ========================================================
    # Read CSV
    # ========================================================

    try:

        df = pd.read_csv(
            uploaded_file
        )

    except Exception as error:

        st.error(
            f"Atlas could not read this CSV file: {error}"
        )

        st.stop()


    st.success(
        f"Dataset uploaded: {uploaded_file.name}"
    )


    # ========================================================
    # Dataset Overview
    # ========================================================

    st.subheader("Dataset Overview")


    pii_columns = [
        column
        for column in df.columns
        if column.lower() in PII_COLUMNS
    ]


    overview_columns = st.columns(3)


    with overview_columns[0]:

        st.metric(
            "Rows",
            len(df),
        )


    with overview_columns[1]:

        st.metric(
            "Columns",
            len(df.columns),
        )


    with overview_columns[2]:

        st.metric(
            "PII Columns",
            len(pii_columns),
        )


    # ========================================================
    # Privacy-safe preview
    # ========================================================

    with st.expander(
        "Preview dataset",
        expanded=True,
    ):

        st.caption(
            "Privacy-safe preview. PII fields are automatically "
            "redacted before display."
        )

        preview_df = create_privacy_safe_preview(
            df
        )

        st.dataframe(
            preview_df,
            use_container_width=True,
            height=360,
        )


    # ========================================================
    # Deterministic analysis
    # ========================================================

    analysis = analyze_dataset(
        df
    )

    findings = analysis[
        "all_findings"
    ]


    # ========================================================
    # Atlas Findings
    # ========================================================

    st.header("Atlas Findings")


    high_findings = [
        finding
        for finding in findings
        if finding.severity.lower() == "high"
    ]


    medium_findings = [
        finding
        for finding in findings
        if finding.severity.lower() == "medium"
    ]


    pii_findings = [
        finding
        for finding in findings
        if finding.issue == "pii_detected"
    ]


    finding_metrics = st.columns(4)


    with finding_metrics[0]:

        st.metric(
            "Total Findings",
            len(findings),
        )


    with finding_metrics[1]:

        st.metric(
            "High Severity",
            len(high_findings),
        )


    with finding_metrics[2]:

        st.metric(
            "Medium Severity",
            len(medium_findings),
        )


    with finding_metrics[3]:

        st.metric(
            "PII Findings",
            len(pii_findings),
        )


    st.divider()


    # ========================================================
    # Findings table
    # ========================================================

    if findings:

        findings_table = []


        for finding in findings:

            findings_table.append(
                {
                    "Category": finding.category,
                    "Issue": finding.issue,
                    "Column": (
                        finding.column
                        if finding.column is not None
                        else "Dataset-level"
                    ),
                    "Severity": finding.severity.upper(),
                    "Count": finding.count,
                }
            )


        findings_df = pd.DataFrame(
            findings_table
        )


        st.dataframe(
            findings_df,
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.success(
            "Atlas did not detect any configured findings."
        )


    # ========================================================
    # Investigate Finding
    # ========================================================

    if findings:

        st.divider()

        st.header("Investigate a Finding")

        st.write(
            "Select a detected finding to inspect its evidence, "
            "governance rationale, and approved remediation guidance."
        )


        finding_options = [
            finding_label(finding)
            for finding in findings
        ]


        selected_label = st.selectbox(
            "Select a finding to investigate",
            finding_options,
        )


        selected_index = finding_options.index(
            selected_label
        )


        selected_finding = findings[
            selected_index
        ]


        # ====================================================
        # Selected Finding
        # ====================================================

        st.subheader("Selected Finding")


        selected_columns = st.columns(4)


        with selected_columns[0]:

            st.caption("Issue")

            st.write(
                selected_finding.issue
            )


        with selected_columns[1]:

            st.caption("Column")

            st.write(
                selected_finding.column
                if selected_finding.column
                else "Dataset-level"
            )


        with selected_columns[2]:

            st.caption("Severity")

            if (
                selected_finding.severity.lower()
                == "high"
            ):

                st.markdown(
                    '<div class="severity-high">HIGH</div>',
                    unsafe_allow_html=True,
                )

            else:

                st.markdown(
                    '<div class="severity-medium">MEDIUM</div>',
                    unsafe_allow_html=True,
                )


        with selected_columns[3]:

            st.caption("Occurrences")

            st.write(
                selected_finding.count
            )


        st.info(
            selected_finding.description
        )


        # ====================================================
        # Evidence
        # ====================================================

        st.subheader("🔎 Evidence")


        raw_evidence = collect_finding_evidence(
            df=df,
            finding=selected_finding,
        )


        sanitized_evidence = sanitize_evidence(
            evidence=raw_evidence,
            finding=selected_finding,
        )


        st.write(
            f"Atlas found {len(sanitized_evidence)} "
            "supporting record(s)."
        )


        if sanitized_evidence:

            for evidence_index, item in enumerate(
                sanitized_evidence,
                start=1,
            ):

                row_number = item[
                    "row_index"
                ]


                with st.expander(
                    f"Row {row_number + 1}",
                    expanded=evidence_index == 1,
                ):

                    st.write(
                        f"**Finding Column:** "
                        f"{item['column']}"
                    )

                    st.write(
                        f"**Finding Value:** "
                        f"{item['value']}"
                    )

                    st.write(
                        "**Sanitized Row Data:**"
                    )

                    st.json(
                        item["row_data"]
                    )

        else:

            st.info(
                "No concrete dataset evidence was collected "
                "for this finding."
            )


        # ====================================================
        # Governance + remediation retrieval
        # ====================================================

        agent, context_builder = (
            create_atlas_components()
        )


        finding_data = {
            "category": selected_finding.category,
            "column": selected_finding.column,
            "issue": selected_finding.issue,
            "count": selected_finding.count,
            "severity": selected_finding.severity,
            "description": selected_finding.description,
        }


        with st.spinner(
            "Retrieving approved governance and remediation knowledge..."
        ):

            selected_context = (
                context_builder.build_context(
                    df=df,
                    finding=finding_data,
                    query=build_governance_query(
                        selected_finding
                    ),
                    top_k=2,
                )
            )


        retrieved_knowledge = (
            selected_context[
                "retrieved_knowledge"
            ]
        )


        governance_knowledge = [
            knowledge
            for knowledge in retrieved_knowledge
            if knowledge.get("category")
            != "remediation"
        ]


        remediation_knowledge = [
            knowledge
            for knowledge in retrieved_knowledge
            if knowledge.get("category")
            == "remediation"
        ]


        # ====================================================
        # Why This Matters
        # ====================================================

        st.subheader("📚 Why This Matters")


        if governance_knowledge:

            for knowledge in governance_knowledge:

                with st.expander(
                    (
                        f"Governance Rule — "
                        f"Chunk {knowledge.get('chunk_id')}"
                    ),
                    expanded=True,
                ):

                    st.markdown(
                        knowledge.get(
                            "content",
                            "",
                        )
                    )

                    st.caption(
                        f"Source: "
                        f"{knowledge.get('source')}"
                    )

                    if knowledge.get(
                        "distance"
                    ) is not None:

                        st.caption(
                            f"Retrieval distance: "
                            f"{knowledge['distance']:.3f}"
                        )

        else:

            st.info(
                "No applicable governance knowledge was retrieved."
            )


        # ====================================================
        # Approved Remediation
        # ====================================================

        st.subheader("🛠️ Approved Remediation")


        if remediation_knowledge:

            for knowledge in remediation_knowledge:

                with st.expander(
                    (
                        f"Approved Remediation Rule — "
                        f"Chunk {knowledge.get('chunk_id')}"
                    ),
                    expanded=True,
                ):

                    st.markdown(
                        knowledge.get(
                            "content",
                            "",
                        )
                    )

                    st.caption(
                        f"Source: "
                        f"{knowledge.get('source')}"
                    )

                    if knowledge.get(
                        "distance"
                    ) is not None:

                        st.caption(
                            f"Retrieval distance: "
                            f"{knowledge['distance']:.3f}"
                        )

        else:

            st.info(
                "No approved remediation guidance was retrieved."
            )


    # ========================================================
    # Ask Atlas
    # ========================================================

    st.divider()

    st.header("🤖 Ask Atlas")

    st.write(
        "Ask Atlas a natural-language question about a "
        "detected data-quality or governance finding."
    )


    question = st.text_input(
        "Your question",
        placeholder=(
            "Why was annual_spend flagged?"
        ),
    )


    st.caption(
        "Examples: Why is email considered PII? "
        "Why is the phone column incomplete? "
        "Why are there duplicate records?"
    )


    if st.button(
        "Ask Atlas",
        type="primary",
    ):

        if not question.strip():

            st.warning(
                "Please enter a question."
            )

        else:

            with st.spinner(
                "Atlas is analyzing your question..."
            ):

                resolver = FindingResolver()


                resolved_finding = resolver.resolve(
                    question=question,
                    findings=findings,
                )


                if resolved_finding is None:

                    st.error(
                        "Atlas could not resolve your question "
                        "to a detected finding."
                    )

                    st.info(
                        "Try asking about a finding that appears "
                        "in the Atlas Findings table."
                    )

                else:

                    # ==================================================
                    # Resolved Finding
                    # ==================================================

                    st.subheader(
                        "Resolved Finding"
                    )


                    resolved_columns = st.columns(4)


                    with resolved_columns[0]:

                        st.caption("Issue")

                        st.write(
                            resolved_finding.issue
                        )


                    with resolved_columns[1]:

                        st.caption("Column")

                        st.write(
                            resolved_finding.column
                            if resolved_finding.column
                            else "Dataset-level"
                        )


                    with resolved_columns[2]:

                        st.caption("Severity")

                        st.write(
                            resolved_finding.severity.upper()
                        )


                    with resolved_columns[3]:

                        st.caption("Count")

                        st.write(
                            resolved_finding.count
                        )


                    # ==================================================
                    # Generate Atlas response
                    # ==================================================

                    agent, _ = (
                        create_atlas_components()
                    )


                    response = agent.explain_finding(
                        df=df,
                        finding=resolved_finding,
                        user_question=question,
                    )


                    st.subheader(
                        "Atlas Response"
                    )


                    st.markdown(
                        response
                    )


    # ========================================================
    # Governance Report
    # ========================================================

    st.divider()

    st.header("📄 Governance Report")

    st.write(
        "Generate a privacy-safe Markdown report containing "
        "the dataset overview, deterministic findings, "
        "sanitized evidence, governance rules, and approved "
        "remediation guidance."
    )


    if st.button(
        "📄 Generate Governance Report",
        type="secondary",
    ):

        with st.spinner(
            "Atlas is preparing your governance report..."
        ):

            _, report_context_builder = (
                create_atlas_components()
            )


            knowledge_by_finding = {}


            for finding in findings:

                finding_data = {
                    "category": finding.category,
                    "column": finding.column,
                    "issue": finding.issue,
                    "count": finding.count,
                    "severity": finding.severity,
                    "description": finding.description,
                }


                finding_key = (
                    f"{finding.issue}|"
                    f"{finding.column or 'dataset'}"
                )


                try:

                    # ==================================================
                    # Targeted governance retrieval
                    # ==================================================

                    governance_query = (
                        build_governance_query(
                            finding
                        )
                    )


                    context = (
                        report_context_builder.build_context(
                            df=df,
                            finding=finding_data,
                            query=governance_query,
                            top_k=2,
                        )
                    )


                    governance_chunks = [
                        knowledge
                        for knowledge in context[
                            "retrieved_knowledge"
                        ]
                        if knowledge.get(
                            "category"
                        ) != "remediation"
                    ]


                    remediation_chunks = [
                        knowledge
                        for knowledge in context[
                            "retrieved_knowledge"
                        ]
                        if knowledge.get(
                            "category"
                        ) == "remediation"
                    ]


                    knowledge_by_finding[
                        finding_key
                    ] = {
                        "governance": governance_chunks,
                        "remediation": remediation_chunks,
                    }


                except Exception:

                    knowledge_by_finding[
                        finding_key
                    ] = {
                        "governance": [],
                        "remediation": [],
                    }


            # ========================================================
            # Generate report
            # ========================================================

            report = generate_governance_report(
                dataset_name=uploaded_file.name,
                df=df,
                analysis=analysis,
                knowledge_by_finding=knowledge_by_finding,
            )


            st.session_state[
                "atlas_governance_report"
            ] = report


            st.success(
                "Governance report generated successfully."
            )


    # ========================================================
    # Download report
    # ========================================================

    if (
        "atlas_governance_report"
        in st.session_state
    ):

        st.download_button(
            label="⬇️ Download Governance Report",
            data=st.session_state[
                "atlas_governance_report"
            ],
            file_name="atlas_governance_report.md",
            mime="text/markdown",
        )


        with st.expander(
            "Preview Governance Report"
        ):

            st.markdown(
                st.session_state[
                    "atlas_governance_report"
                ]
            )


# ============================================================
# Footer
# ============================================================

st.divider()

st.caption(
    "Atlas • Enterprise Data Intelligence & Governance Copilot"
)

st.caption(
    "Deterministic findings → "
    "Sanitized evidence → "
    "Governance retrieval → "
    "Grounded AI explanation"
)