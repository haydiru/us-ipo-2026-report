"""Domain schemas, constants, and frozen Pydantic models for IPO Ledger."""

from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SHEET_IPO_REPORT = "IPO_Report"
SHEET_AUDIT_SUMMARY = "Audit_Summary"
SHEET_DISCREPANCY_LOG = "Discrepancy_Log"
SHEET_EXCLUSIONS = "Exclusions"
SHEET_SOURCE_EVIDENCE = "Source_Evidence"
SHEET_RUN_METADATA = "Run_Metadata"

ALL_SHEET_NAMES = [
    SHEET_IPO_REPORT,
    SHEET_AUDIT_SUMMARY,
    SHEET_DISCREPANCY_LOG,
    SHEET_EXCLUSIONS,
    SHEET_SOURCE_EVIDENCE,
    SHEET_RUN_METADATA,
]

W1_COLUMNS = [
    "Company",
    "Ticker",
    "Exchange",
    "Pricing Date",
    "Offer Price",
    "Base Shares Offered",
    "Gross Offering Amount",
    "SEC Final Prospectus",
    "Form Type",
    "Accession No.",
    "Security Type",
    "Is_SPAC",
    "Status",
    "Flag Codes",
]

W3_COLUMNS = [
    "Record Key",
    "Field",
    "Primary Value",
    "Secondary Value",
    "Source URLs",
    "Resolution",
    "Rationale",
    "Resolver",
]

W4_COLUMNS = [
    "Accession No.",
    "Company",
    "Reason Code",
    "Evidence Link",
]

W5_COLUMNS = [
    "Record Key",
    "Field",
    "Value",
    "Source URL",
    "Doc SHA256",
    "Char Offset",
    "Snippet",
    "Retrieval Timestamp",
]

W6_COLUMNS = [
    "Parameter",
    "Value",
]


class ImmutableModel(BaseModel):
    """Base frozen model forbidding extra attributes."""

    model_config = ConfigDict(frozen=True, extra="forbid")


class CandidateModel(ImmutableModel):
    """Discovered filing candidate."""

    accession_no: str
    run_id: str
    cik: str
    company_name: str
    form_type: str
    filing_date: date
    classification: Literal["IPO", "EXCLUDED"]


class ExclusionModel(ImmutableModel):
    """Filing excluded from the qualifying universe."""

    accession_no: str
    run_id: str
    company_name: str
    reason_code: Literal[
        "FOLLOW_ON",
        "DIRECT_LISTING",
        "DE_SPAC",
        "FUND",
        "WRONG_VENUE",
        "UNPRICED",
        "DUPLICATE",
        "WITHDRAWN",
        "OTHER",
    ]
    evidence_url: str


class EvidenceModel(ImmutableModel):
    """Field-level verbatim extraction provenance."""

    evidence_id: int
    cik: str
    field_name: str
    value: str
    source_url: str
    doc_sha256: str
    char_offset: int
    snippet: str
    retrieval_timestamp: str


class CrossCheckModel(ImmutableModel):
    """Secondary source verification record."""

    check_id: int
    cik: str
    source_name: str
    source_url: str
    retrieved_at: str
    values_json: str
    all_fields_match: bool


class DiscrepancyModel(ImmutableModel):
    """Discrepancy record between primary and secondary sources."""

    discrepancy_id: int
    cik: str
    field_name: str
    primary_value: str
    secondary_value: str
    source_urls: str
    resolution: str
    rationale: str
    resolver: Literal["rule", "reviewer"]


class AuditResultModel(ImmutableModel):
    """Mathematical recompute audit record."""

    cik: str
    gross_primary: Decimal
    gross_recompute: Decimal
    delta: Decimal
    passed: bool


class IpoRecordModel(ImmutableModel):
    """Qualifying IPO record."""

    cik: str
    accession_no: str
    company_name: str
    ticker: str
    exchange: str
    pricing_date: date
    offer_price: Decimal
    base_shares: int
    overallotment_shares: int | None = None
    gross_offering_amount: Decimal
    form_type: str
    security_type: str = "Common Stock"
    is_spac: bool = False
    prospectus_url: str
    status: Literal["VERIFIED", "FLAGGED"]
    flag_codes: str = ""


class GateResultModel(ImmutableModel):
    """Completeness gate evaluation result."""

    run_id: str
    universe_reconciled: bool
    urls_valid: bool
    no_manual_queue: bool
    calc_audit_passed: bool
    no_duplicates: bool
    crosscheck_complete: bool
    verdict: Literal["VERIFIED", "DRAFT_INCOMPLETE"]
    blockers: list[str] = Field(default_factory=list)


class RunManifestModel(ImmutableModel):
    """Frozen run manifest metadata."""

    run_id: str
    as_of_date: date
    rule_hash: str
    tool_versions: dict[str, str]
    edgar_user_agent: str
    status: Literal["ready", "config_invalid", "running", "completed"]
    created_at: str
