from dotenv import load_dotenv

load_dotenv()

from app.ingestion.loader import load_csv
from app.governance.analyzer import analyze_dataset
from app.governance.resolver import FindingResolver
from app.retrieval.vector_store import KnowledgeVectorStore
from app.retrieval.retriever import KnowledgeRetriever
from app.agents.context_builder import GovernanceContextBuilder
from app.llm.client import LLMClient
from app.agents.governance_agent import GovernanceAgent


# --------------------------------------------------
# 1. Load the real dataset
# --------------------------------------------------

dataset_path = "data/raw/customers.csv"

df = load_csv(dataset_path)

print("\n=== ATLAS DATASET ===")
print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")


# --------------------------------------------------
# 2. Run deterministic analysis
# --------------------------------------------------

analysis = analyze_dataset(df)

findings = analysis["all_findings"]

print("\n=== ATLAS FINDINGS ===")
print(f"Total findings: {len(findings)}")


# --------------------------------------------------
# 3. Create the finding resolver
# --------------------------------------------------

resolver = FindingResolver()


# --------------------------------------------------
# 4. Accept a natural-language user question
# --------------------------------------------------

user_question = "Why was annual_spend flagged?"


print("\n=== USER QUESTION ===")
print(user_question)


# --------------------------------------------------
# 5. Resolve the question to an AtlasFinding
# --------------------------------------------------

finding = resolver.resolve(
    question=user_question,
    findings=findings,
)

if finding is None:
    raise ValueError(
        "Atlas could not identify a relevant finding "
        "for the user's question."
    )


print("\n=== RESOLVED FINDING ===")
print(finding)


# --------------------------------------------------
# 6. Create retrieval components
# --------------------------------------------------

vector_store = KnowledgeVectorStore()

retriever = KnowledgeRetriever(
    vector_store
)

context_builder = GovernanceContextBuilder(
    retriever
)


# --------------------------------------------------
# 7. Create the Governance Agent
# --------------------------------------------------

llm_client = LLMClient()

agent = GovernanceAgent(
    context_builder=context_builder,
    llm_client=llm_client,
)


# --------------------------------------------------
# 8. Generate the grounded answer
# --------------------------------------------------

response = agent.explain_finding(
    df=df,
    finding=finding,
    user_question=user_question,
)


# --------------------------------------------------
# 9. Display the final Atlas response
# --------------------------------------------------

print("\n=== ATLAS RESPONSE ===")
print(response)