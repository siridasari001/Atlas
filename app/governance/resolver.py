import re

from app.models.metadata import AtlasFinding


class FindingResolver:
    """
    Resolve a user's natural-language question to the most relevant
    deterministic AtlasFinding.
    """

    ISSUE_ALIASES = {
        "pii_detected": {
            "pii",
            "personal information",
            "personally identifiable information",
            "personally identifiable",
            "sensitive information",
            "why is this sensitive",
        },
        "missing_values": {
            "missing",
            "missing value",
            "missing values",
            "incomplete",
            "completeness",
            "why is this missing",
        },
        "duplicate_records": {
            "duplicate",
            "duplicates",
            "duplicate record",
            "duplicate records",
            "duplicated",
        },
        "invalid_negative_value": {
            "negative",
            "negative value",
            "negative values",
            "annual spend",
            "invalid negative",
        },
    }

    def resolve(
        self,
        question: str,
        findings: list[AtlasFinding],
    ) -> AtlasFinding | None:
        """
        Find the most relevant finding based on terms in the question.

        Args:
            question: User's natural-language question.
            findings: Available normalized AtlasFinding objects.

        Returns:
            The best matching AtlasFinding, or None if no match exists.
        """

        question_text = question.lower()

        # --------------------------------------------------
        # 1. Find findings whose column is explicitly mentioned
        # --------------------------------------------------

        column_matches = []

        for finding in findings:
            if finding.column is None:
                continue

            column_name = finding.column.lower()

            if re.search(
                rf"\b{re.escape(column_name)}\b",
                question_text,
            ):
                column_matches.append(finding)

        # --------------------------------------------------
        # 2. If a column was mentioned, only search findings
        #    associated with that column.
        # --------------------------------------------------

        if column_matches:

            # Exact issue phrase
            for finding in column_matches:
                issue_terms = finding.issue.lower().replace("_", " ")

                if issue_terms in question_text:
                    return finding

            # Natural-language aliases
            for finding in column_matches:
                aliases = self.ISSUE_ALIASES.get(
                    finding.issue.lower(),
                    set(),
                )

                for alias in aliases:
                    if alias in question_text:
                        return finding

            # If the user explicitly names a column and asks
            # why it was flagged, use the finding associated
            # with that column.
            flagging_terms = {
                "flagged",
                "flag",
                "issue",
                "wrong",
                "problem",
            }

            if any(
                term in question_text
                for term in flagging_terms
            ):
                return column_matches[0]

            # A column was explicitly mentioned, but no matching
            # issue was found. Do not guess.
            return None

        # --------------------------------------------------
        # 3. No specific column was mentioned.
        #    Try matching issue semantics across all findings.
        # --------------------------------------------------

        for finding in findings:
            issue_terms = finding.issue.lower().replace("_", " ")

            if issue_terms in question_text:
                return finding

            aliases = self.ISSUE_ALIASES.get(
                finding.issue.lower(),
                set(),
            )

            for alias in aliases:
                if alias in question_text:
                    return finding

        # --------------------------------------------------
        # 4. No deterministic match found
        # --------------------------------------------------

        return None