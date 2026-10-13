from pydantic import BaseModel


PII_COLUMNS = {
    "email",
    "phone",
    "date_of_birth",
}


class ColumnProfile(BaseModel):
    name: str
    data_type: str
    missing_count: int
    unique_count: int


class DatasetProfile(BaseModel):
    row_count: int
    column_count: int
    columns: list[ColumnProfile]


class QualityFinding(BaseModel):
    column: str | None = None
    issue: str
    count: int
    severity: str
    description: str


class PIIClassification(BaseModel):
    column: str
    classification: str
    reason: str


class AtlasFinding(BaseModel):
    """
    Unified representation of a governance or data-quality finding.
    """

    category: str
    column: str | None = None
    issue: str
    count: int
    severity: str
    description: str


class KnowledgeChunk(BaseModel):
    content: str
    source: str
    chunk_id: int
    category: str