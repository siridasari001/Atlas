from app.ingestion.loader import load_csv
from app.governance.analyzer import analyze_dataset
from app.governance.evidence import collect_finding_evidence
from app.governance.sanitizer import sanitize_evidence


# --------------------------------------------------
# 1. Load dataset
# --------------------------------------------------

df = load_csv("data/raw/customers.csv")


# --------------------------------------------------
# 2. Analyze dataset
# --------------------------------------------------

analysis = analyze_dataset(df)

findings = analysis["all_findings"]


# --------------------------------------------------
# 3. Find duplicate-record finding
# --------------------------------------------------

duplicate_finding = next(
    finding
    for finding in findings
    if finding.issue == "duplicate_records"
)

print("\n=== DUPLICATE FINDING ===")
print(duplicate_finding)


# --------------------------------------------------
# 4. Collect duplicate evidence
# --------------------------------------------------

evidence = collect_finding_evidence(
    df=df,
    finding=duplicate_finding,
)

print("\n=== DUPLICATE EVIDENCE ===")
print(f"Evidence records: {len(evidence)}")

for item in evidence:
    print("\n--- Evidence Record ---")
    print(f"Row index: {item['row_index']}")
    print(f"Row data: {item['row_data']}")


# --------------------------------------------------
# 5. Sanitize duplicate evidence
# --------------------------------------------------

sanitized = sanitize_evidence(
    evidence=evidence,
    finding=duplicate_finding,
)

print("\n=== SANITIZED DUPLICATE EVIDENCE ===")

for item in sanitized:
    print("\n--- Evidence Record ---")
    print(f"Row index: {item['row_index']}")
    print(f"Row data: {item['row_data']}")