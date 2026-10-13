from datetime import datetime

import pandas as pd

from app.governance.evidence import collect_finding_evidence
from app.governance.sanitizer import sanitize_evidence
from app.models.metadata import AtlasFinding


def generate_governance_report(
    dataset_name: str,
    df: pd.DataFrame,
    analysis: dict,
    knowledge_by_finding: dict | None = None,
) -> str:
    """
    Generate a privacy-safe Markdown governance report.

    The report contains:
    - Dataset overview
    - Finding summary
    - Deterministic findings
    - Sanitized evidence
    - Retrieved governance knowledge
    - Retrieved remediation knowledge

    Raw PII is never included in the report.

    Args:
        dataset_name:
            Name of the analyzed dataset.

        df:
            Dataset being analyzed.

        analysis:
            Output returned by analyze_dataset().

        knowledge_by_finding:
            Optional dictionary containing retrieved governance
            and remediation knowledge for each finding.

    Returns:
        A Markdown-formatted governance report.
    """

    if knowledge_by_finding is None:
        knowledge_by_finding = {}

    findings: list[AtlasFinding] = analysis.get(
        "all_findings",
        [],
    )

    high_severity_count = sum(
        1
        for finding in findings
        if finding.severity.lower() == "high"
    )

    medium_severity_count = sum(
        1
        for finding in findings
        if finding.severity.lower() == "medium"
    )

    pii_count = sum(
        1
        for finding in findings
        if finding.issue == "pii_detected"
    )

    generated_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    report_lines: list[str] = []

    # --------------------------------------------------
    # Report header
    # --------------------------------------------------

    report_lines.extend(
        [
            "# Atlas Governance Report",
            "",
            "## Report Information",
            "",
            f"- **Dataset:** `{dataset_name}`",
            f"- **Generated:** `{generated_at}`",
            "- **Privacy:** PII fields are automatically redacted.",
            "",
        ]
    )

    # --------------------------------------------------
    # Dataset overview
    # --------------------------------------------------

    report_lines.extend(
        [
            "## Dataset Overview",
            "",
            f"- **Rows:** {len(df)}",
            f"- **Columns:** {len(df.columns)}",
            f"- **Total Findings:** {len(findings)}",
            f"- **High Severity Findings:** {high_severity_count}",
            f"- **Medium Severity Findings:** {medium_severity_count}",
            f"- **PII Findings:** {pii_count}",
            "",
        ]
    )

    # --------------------------------------------------
    # Column information
    # --------------------------------------------------

    report_lines.extend(
        [
            "### Dataset Columns",
            "",
        ]
    )

    for column in df.columns:
        report_lines.append(
            f"- `{column}`"
        )

    report_lines.append("")

    # --------------------------------------------------
    # Privacy notice
    # --------------------------------------------------

    report_lines.extend(
        [
            "## Privacy & Security",
            "",
            "Atlas applies privacy-safe handling to evidence "
            "before it is included in downstream explanations "
            "or reports.",
            "",
            "Known PII fields are redacted before evidence is "
            "displayed or passed to downstream AI components.",
            "",
            "**PII is never reconstructed or exposed by the "
            "report generator.**",
            "",
        ]
    )

    # --------------------------------------------------
    # Findings summary
    # --------------------------------------------------

    report_lines.extend(
        [
            "## Findings Summary",
            "",
            "| Category | Issue | Column | Severity | Count |",
            "|---|---|---|---|---:|",
        ]
    )

    for finding in findings:
        column = (
            finding.column
            if finding.column is not None
            else "Dataset-level"
        )

        report_lines.append(
            f"| {finding.category} "
            f"| {finding.issue} "
            f"| {column} "
            f"| {finding.severity.upper()} "
            f"| {finding.count} |"
        )

    report_lines.append("")

    # --------------------------------------------------
    # Detailed findings
    # --------------------------------------------------

    report_lines.extend(
        [
            "## Detailed Findings",
            "",
        ]
    )

    if not findings:
        report_lines.extend(
            [
                "Atlas did not detect any configured findings.",
                "",
            ]
        )

    for index, finding in enumerate(
        findings,
        start=1,
    ):
        column = (
            finding.column
            if finding.column is not None
            else "Dataset-level"
        )

        report_lines.extend(
            [
                f"### Finding {index}: {finding.issue}",
                "",
                f"- **Category:** `{finding.category}`",
                f"- **Column:** `{column}`",
                f"- **Severity:** `{finding.severity.upper()}`",
                f"- **Count:** `{finding.count}`",
                f"- **Description:** {finding.description}",
                "",
            ]
        )

        # --------------------------------------------------
        # Evidence
        # --------------------------------------------------

        report_lines.extend(
            [
                "#### Sanitized Evidence",
                "",
            ]
        )

        raw_evidence = collect_finding_evidence(
            df=df,
            finding=finding,
        )

        sanitized_evidence = sanitize_evidence(
            evidence=raw_evidence,
            finding=finding,
        )

        if not sanitized_evidence:
            report_lines.extend(
                [
                    "No concrete dataset evidence was collected.",
                    "",
                ]
            )

        else:
            for evidence_index, item in enumerate(
                sanitized_evidence,
                start=1,
            ):
                report_lines.extend(
                    [
                        f"**Evidence Record {evidence_index}**",
                        "",
                        f"- **Row Index:** `{item['row_index']}`",
                        f"- **Finding Column:** "
                        f"`{item['column']}`",
                        f"- **Finding Value:** "
                        f"`{item['value']}`",
                        "",
                        "**Sanitized Row Data:**",
                        "",
                        "```text",
                        str(item["row_data"]),
                        "```",
                        "",
                    ]
                )

        # --------------------------------------------------
        # Retrieved knowledge
        # --------------------------------------------------

        finding_key = (
            f"{finding.issue}|"
            f"{finding.column or 'dataset'}"
        )

        knowledge = knowledge_by_finding.get(
            finding_key,
            {},
        )

        governance_knowledge = knowledge.get(
            "governance",
            [],
        )

        remediation_knowledge = knowledge.get(
            "remediation",
            [],
        )

        # --------------------------------------------------
        # Governance knowledge
        # --------------------------------------------------

        report_lines.extend(
            [
                "#### Governance Knowledge",
                "",
            ]
        )

        if not governance_knowledge:
            report_lines.extend(
                [
                    "No governance knowledge was retrieved.",
                    "",
                ]
            )

        else:
            for chunk in governance_knowledge:
                report_lines.extend(
                    [
                        f"**Source:** `{chunk.get('source')}`  ",
                        f"**Chunk:** `{chunk.get('chunk_id')}`",
                        "",
                        chunk.get(
                            "content",
                            "",
                        ),
                        "",
                    ]
                )

        # --------------------------------------------------
        # Remediation knowledge
        # --------------------------------------------------

        report_lines.extend(
            [
                "#### Approved Remediation",
                "",
            ]
        )

        if not remediation_knowledge:
            report_lines.extend(
                [
                    "No approved remediation guidance was retrieved.",
                    "",
                ]
            )

        else:
            for chunk in remediation_knowledge:
                report_lines.extend(
                    [
                        f"**Source:** `{chunk.get('source')}`  ",
                        f"**Chunk:** `{chunk.get('chunk_id')}`",
                        "",
                        chunk.get(
                            "content",
                            "",
                        ),
                        "",
                    ]
                )

    # --------------------------------------------------
    # Footer
    # --------------------------------------------------

    report_lines.extend(
        [
            "---",
            "",
            "## Atlas Governance Notice",
            "",
            "This report contains deterministic Atlas findings "
            "and privacy-sanitized evidence.",
            "",
            "Atlas does not automatically modify source data.",
            "Approved remediation guidance should be followed "
            "according to the applicable governance rules and "
            "data-owner approval requirements.",
            "",
            "Generated by **Atlas — Enterprise Data Intelligence "
            "& Governance Copilot**.",
        ]
    )

    return "\n".join(report_lines)