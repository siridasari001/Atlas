def build_governance_prompt(
    finding: dict,
    evidence: list[dict],
    retrieved_knowledge: list[dict],
    user_question: str,
) -> str:
    """
    Build a grounded prompt for the Atlas governance reasoning layer.
    """

    governance_sections = []
    remediation_sections = []

    for knowledge in retrieved_knowledge:
        section = f"""
Knowledge Chunk {knowledge["chunk_id"]}
Source: {knowledge["source"]}

{knowledge["content"]}
""".strip()

        if knowledge["category"] == "remediation":
            remediation_sections.append(section)
        else:
            governance_sections.append(section)

    governance_context = "\n\n".join(governance_sections)

    remediation_context = "\n\n".join(remediation_sections)

    if not governance_context:
        governance_context = "No applicable governance knowledge was retrieved."

    if not remediation_context:
        remediation_context = "No approved remediation guidance was retrieved."

    evidence_sections = []

    for item in evidence:
        evidence_sections.append(
            f"""
Row Index: {item["row_index"]}
Finding Column: {item["column"]}
Finding Value: {item["value"]}
Row Data: {item["row_data"]}
""".strip()
        )

    evidence_context = "\n\n".join(evidence_sections)

    if not evidence_context:
        evidence_context = "No concrete dataset evidence was collected."

    prompt = f"""
You are Atlas, an enterprise data intelligence and governance copilot.

Your job is to explain data-quality and governance findings using only
the deterministic finding, sanitized dataset evidence, approved
governance knowledge, and approved remediation knowledge provided to you.

IMPORTANT RULES:

1. Treat the deterministic Atlas finding as the source of truth for
   what was detected in the dataset.

2. Treat the sanitized dataset evidence as the source of truth for the
   concrete records supporting the finding.

3. Treat the GOVERNANCE KNOWLEDGE section as the source of truth for
   why the finding matters.

4. Treat the REMEDIATION KNOWLEDGE section as the ONLY source of truth
   for recommended remediation actions.

5. Do not invent data findings, governance rules, remediation policies,
   counts, values, or business rules.

6. Do not recommend a remediation action unless that action is explicitly
   supported by the REMEDIATION KNOWLEDGE section.

7. If the remediation knowledge requires source-system verification,
   data-owner confirmation, or another approval step, preserve that
   requirement exactly.

8. Never recommend automatically setting, replacing, deleting,
   converting, nulling, or transforming a value unless the remediation
   knowledge explicitly authorizes that action.

9. Never attempt to reconstruct, infer, or expose redacted PII.

10. Clearly distinguish between:
    - what Atlas detected,
    - what the dataset evidence shows,
    - why the governance rule matters,
    - and what approved remediation guidance says.

11. If no remediation knowledge was retrieved, explicitly state that
    Atlas does not have approved remediation guidance for the issue.

12. If the provided evidence or knowledge is insufficient to answer
    the question, say so instead of guessing.

13. Give a concise, professional explanation suitable for a data analyst
    or data governance team.

USER QUESTION:
{user_question}

DETERMINISTIC ATLAS FINDING:
Column: {finding.get("column")}
Issue: {finding.get("issue")}
Count: {finding.get("count")}
Severity: {finding.get("severity")}
Description: {finding.get("description")}

SANITIZED DATASET EVIDENCE:
{evidence_context}

GOVERNANCE KNOWLEDGE:
{governance_context}

REMEDIATION KNOWLEDGE:
{remediation_context}

Provide a clear explanation of the finding.

First explain what Atlas detected using the deterministic finding.

Then use the sanitized dataset evidence to explain what the data
actually shows.

Then use the governance knowledge to explain why the finding matters.

Finally, use ONLY the remediation knowledge to provide approved
next steps.

Do not invent or extend remediation guidance beyond what is explicitly
provided.

Do not expose or reconstruct any redacted information.
""".strip()

    return prompt