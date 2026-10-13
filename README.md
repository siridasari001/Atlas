# Atlas — Enterprise Data Intelligence & Governance Copilot

Atlas is a Python-based data intelligence and governance copilot that combines deterministic data-quality checks, privacy-safe evidence handling, governance knowledge retrieval, and grounded LLM reasoning.

It is designed to help data analysts and governance teams understand **what went wrong, why it matters, what evidence supports the finding, and what approved remediation guidance applies**.

## ✨ Key Features

- **Data profiling** — summarizes dataset structure, data types, missing values, and uniqueness.
- **Deterministic data-quality detection** — identifies missing values, duplicate records, and invalid negative annual spend.
- **PII detection** — identifies sensitive customer fields such as email, phone, and date of birth.
- **Natural-language finding resolution** — maps user questions to the most relevant Atlas finding.
- **Privacy-safe evidence** — redacts PII before evidence is passed to downstream AI components.
- **Hybrid governance reasoning** — combines deterministic findings with retrieved governance and remediation knowledge.
- **Grounded LLM explanations** — uses approved governance and remediation knowledge instead of allowing the model to invent policies.
- **Governance reporting** — generates a structured governance report with findings, evidence, governance rules, and remediation guidance.
- **Streamlit interface** — provides an interactive interface for uploading datasets, reviewing findings, asking Atlas questions, and generating reports.
- **Automated testing** — includes unit, integration, privacy, retrieval, agent, pipeline, and live LLM tests.

## 🏗️ Architecture

```text
                    ┌─────────────────────┐
                    │   CSV Dataset       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Data Profiling      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Deterministic       │
                    │ Governance Checks   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Atlas Findings      │
                    └──────────┬──────────┘
                               │
                ┌──────────────┴──────────────┐
                ▼                             ▼
      ┌──────────────────┐          ┌──────────────────┐
      │ Finding Resolver │          │ Evidence         │
      │                  │          │ Collection       │
      └────────┬─────────┘          └────────┬─────────┘
               │                             │
               │                             ▼
               │                    ┌──────────────────┐
               │                    │ PII Sanitization │
               │                    └────────┬─────────┘
               │                             │
               └──────────────┬──────────────┘
                              ▼
                    ┌─────────────────────┐
                    │ Governance +        │
                    │ Remediation         │
                    │ Knowledge Retrieval │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Grounded Prompt     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ OpenAI LLM          │
                    │ Reasoning Layer     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Atlas Explanation   │
                    │ / Report / UI       │
                    └─────────────────────┘
```

## 🔐 Governance-First Design

Atlas follows a deliberate separation between deterministic detection and AI reasoning.

The deterministic layer establishes **what was actually detected** in the dataset.

The retrieval layer supplies approved governance and remediation knowledge.

The LLM is then used to explain the finding using that structured evidence and knowledge.

This helps prevent the AI layer from inventing findings, policies, remediation actions, or sensitive information.

### Privacy protection

Known PII columns are redacted before evidence is passed to the AI reasoning layer.

For example:

```text
email: [REDACTED]
phone: [REDACTED]
date_of_birth: [REDACTED]
```

Atlas also explicitly instructs the LLM not to reconstruct or expose redacted PII.

## 🧠 Example Findings

The included demonstration dataset contains intentionally introduced issues:

| Finding | Severity | Count |
|---|---:|---:|
| Missing `email` | Medium | 1 |
| Missing `phone` | Medium | 1 |
| Missing `date_of_birth` | Medium | 1 |
| Duplicate records | High | 1 |
| Negative `annual_spend` | High | 1 |
| PII in `email` | High | 1 |
| PII in `phone` | High | 1 |
| PII in `date_of_birth` | High | 1 |

Atlas uses governance rules and approved remediation rules stored in:

```text
data/knowledge/
├── governance_rules.md
└── remediation_rules.md
```

## 🛠️ Tech Stack

- **Python**
- **Pandas**
- **Pydantic / Pydantic Settings**
- **ChromaDB**
- **OpenAI API**
- **Streamlit**
- **pytest**
- **python-dotenv**

## 📁 Project Structure

```text
Atlas/
├── app/
│   ├── agents/
│   │   ├── context_builder.py
│   │   └── governance_agent.py
│   ├── core/
│   │   └── config.py
│   ├── governance/
│   │   ├── analyzer.py
│   │   ├── evidence.py
│   │   ├── findings.py
│   │   ├── pii.py
│   │   ├── quality.py
│   │   ├── resolver.py
│   │   └── sanitizer.py
│   ├── ingestion/
│   │   └── loader.py
│   ├── llm/
│   │   ├── client.py
│   │   └── prompts.py
│   ├── models/
│   │   └── metadata.py
│   ├── profiling/
│   │   └── profiler.py
│   ├── reporting/
│   │   └── report_generator.py
│   └── retrieval/
│       ├── chunker.py
│       ├── loader.py
│       ├── retriever.py
│       └── vector_store.py
├── data/
│   ├── knowledge/
│   │   ├── governance_rules.md
│   │   └── remediation_rules.md
│   └── raw/
│       └── customers.csv
├── streamlit_app/
│   └── app.py
├── tests/
├── index_knowledge.py
├── main.py
├── requirements.txt
└── .env.example
```

## 🚀 Setup

### 1. Clone the repository

```bash
git clone https://github.com/siridasari001/Atlas.git
cd Atlas
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root based on `.env.example`.

Set:

```text
ATLAS_ENV=development
LLM_PROVIDER=openai
OPENAI_API_KEY=your_api_key_here
```

Never commit `.env` or expose your API key.

### 5. Build the knowledge index

```bash
python index_knowledge.py
```

This indexes the governance and remediation knowledge into the local ChromaDB vector store.

## ▶️ Run Atlas

Launch the Streamlit application:

```bash
streamlit run streamlit_app/app.py
```

Then open the local Streamlit URL shown in the terminal.

## 🧪 Testing

Run the complete offline-safe test suite:

```bash
python -m pytest -v
```

Live LLM integration tests can be explicitly enabled with:

```bash
python -m pytest -v --run-live-llm
```

The current test suite contains **28 tests**, including governance, privacy, retrieval, context-building, LLM, agent, multi-question, and end-to-end pipeline coverage.

## 🔎 Example Workflow

1. Upload a CSV dataset.
2. Atlas profiles the dataset.
3. Deterministic governance checks identify findings.
4. Atlas resolves a user's natural-language question to a finding.
5. Supporting dataset evidence is collected.
6. PII is sanitized.
7. Relevant governance and remediation rules are retrieved.
8. The LLM generates a grounded explanation.
9. Atlas can present the finding and generate a governance report.

Example question:

```text
Why was annual_spend flagged?
```

Atlas can identify the deterministic `invalid_negative_value` finding, use the relevant dataset evidence, retrieve the annual-spend governance rule, retrieve approved remediation guidance, and generate a concise explanation.

## 📊 Design Principles

### Deterministic before generative

Critical findings are detected using explicit rules before AI reasoning occurs.

### Evidence before explanation

The LLM receives structured evidence supporting the finding.

### Retrieval before recommendation

Remediation recommendations must come from approved remediation knowledge.

### Privacy before AI

Known PII is sanitized before evidence reaches the AI reasoning layer.

### No invented policy

If Atlas does not have sufficient approved knowledge, it is instructed to say so rather than guess.

## 🔮 Future Enhancements

Potential future directions include:

- Additional data-quality rules
- More sophisticated schema validation
- Role-based governance controls
- Additional enterprise data sources
- Expanded knowledge bases
- Queryable governance history
- More advanced anomaly detection
- API endpoints for programmatic access
- Production deployment and observability

## 👩‍💻 Author

**Siri Chandana Dasari**

Master's in Computer Science  
University of North Texas

---

Built as an enterprise-focused portfolio project combining **Data Engineering, Data Quality, Data Governance, Retrieval-Augmented Generation, Privacy, and LLM applications**.
