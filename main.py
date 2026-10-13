from dotenv import load_dotenv

load_dotenv()

from app.core.config import settings
from app.ingestion.loader import load_csv
from app.profiling.profiler import profile_dataset
from app.governance.analyzer import analyze_dataset
from app.retrieval.loader import load_knowledge_document
from app.retrieval.chunker import chunk_markdown_document


print("Atlas is starting...")
print(f"Environment: {settings.atlas_env}")
print(f"LLM Provider: {settings.llm_provider}")
print(f"OpenAI API key loaded: {bool(settings.openai_api_key)}")


# --------------------------------------------------
# 1. Load dataset
# --------------------------------------------------

dataset_path = "data/raw/customers.csv"

df = load_csv(dataset_path)

print("\nDataset loaded successfully!")
print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")
print(f"Column names: {list(df.columns)}")


# --------------------------------------------------
# 2. Profile dataset
# --------------------------------------------------

profile = profile_dataset(df)

print("\nDataset Profile:")
print(f"Rows: {profile.row_count}")
print(f"Columns: {profile.column_count}")

for column in profile.columns:
    print(
        f"{column.name}: "
        f"type={column.data_type}, "
        f"missing={column.missing_count}, "
        f"unique={column.unique_count}"
    )


# --------------------------------------------------
# 3. Run deterministic governance analysis
# --------------------------------------------------

analysis = analyze_dataset(df)


print("\nData Quality Findings:")

for finding in analysis["quality_findings"]:
    print(
        f"{finding.column}: "
        f"{finding.issue}, "
        f"count={finding.count}, "
        f"severity={finding.severity}"
    )


print("\nDuplicate Findings:")

for finding in analysis["duplicate_findings"]:
    print(
        f"{finding.issue}: "
        f"count={finding.count}, "
        f"severity={finding.severity}"
    )


print("\nInvalid Value Findings:")

for finding in analysis["invalid_findings"]:
    print(
        f"{finding.column}: "
        f"{finding.issue}, "
        f"count={finding.count}, "
        f"severity={finding.severity}"
    )


print("\nPII Findings:")

for finding in analysis["pii_findings"]:
    print(
        f"{finding.column}: "
        f"{finding.classification} - "
        f"{finding.reason}"
    )


# --------------------------------------------------
# 4. Load governance knowledge
# --------------------------------------------------

knowledge_path = "data/knowledge/governance_rules.md"

knowledge = load_knowledge_document(knowledge_path)

print("\nKnowledge Document Loaded Successfully.")


# --------------------------------------------------
# 5. Create knowledge chunks
# --------------------------------------------------

chunks = chunk_markdown_document(
    knowledge,
    knowledge_path,
)

print(f"\nKnowledge Chunks Created: {len(chunks)}")

for chunk in chunks:
    print(f"\n--- Chunk {chunk.chunk_id} ---")
    print(f"Source: {chunk.source}")
    print(f"Category: {chunk.category}")
    print(chunk.content)