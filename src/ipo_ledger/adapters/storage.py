"""SQLite storage repository for relational run persistence (PRD Section 6)."""

import sqlite3
from pathlib import Path

from ipo_ledger.domain.schema import (
    AuditResultModel,
    CandidateModel,
    CrossCheckModel,
    DiscrepancyModel,
    EvidenceModel,
    ExclusionModel,
    GateResultModel,
    IpoRecordModel,
    RunManifestModel,
)


class LedgerStorage:
    """Relational SQLite database repository for pipeline entities."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.executescript("""
            CREATE TABLE IF NOT EXISTS runs (
                run_id TEXT PRIMARY KEY,
                as_of_date TEXT NOT NULL,
                rule_hash TEXT NOT NULL,
                edgar_user_agent TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS candidates (
                accession_no TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                cik TEXT NOT NULL,
                company_name TEXT NOT NULL,
                form_type TEXT NOT NULL,
                filing_date TEXT NOT NULL,
                classification TEXT NOT NULL,
                FOREIGN KEY (run_id) REFERENCES runs (run_id)
            );

            CREATE TABLE IF NOT EXISTS exclusions (
                accession_no TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                company_name TEXT NOT NULL,
                reason_code TEXT NOT NULL,
                evidence_url TEXT NOT NULL,
                FOREIGN KEY (run_id) REFERENCES runs (run_id)
            );

            CREATE TABLE IF NOT EXISTS ipo_records (
                cik TEXT PRIMARY KEY,
                accession_no TEXT NOT NULL,
                company_name TEXT NOT NULL,
                ticker TEXT NOT NULL,
                exchange TEXT NOT NULL,
                pricing_date TEXT NOT NULL,
                offer_price TEXT NOT NULL,
                base_shares INTEGER NOT NULL,
                overallotment_shares INTEGER,
                gross_offering_amount TEXT NOT NULL,
                form_type TEXT NOT NULL,
                security_type TEXT NOT NULL,
                is_spac INTEGER NOT NULL,
                prospectus_url TEXT NOT NULL,
                status TEXT NOT NULL,
                flag_codes TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS evidence (
                evidence_id INTEGER PRIMARY KEY,
                cik TEXT NOT NULL,
                field_name TEXT NOT NULL,
                value TEXT NOT NULL,
                source_url TEXT NOT NULL,
                doc_sha256 TEXT NOT NULL,
                char_offset INTEGER NOT NULL,
                snippet TEXT NOT NULL,
                retrieval_timestamp TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS cross_checks (
                check_id INTEGER PRIMARY KEY,
                cik TEXT NOT NULL,
                source_name TEXT NOT NULL,
                source_url TEXT NOT NULL,
                retrieved_at TEXT NOT NULL,
                values_json TEXT NOT NULL,
                all_fields_match INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS discrepancies (
                discrepancy_id INTEGER PRIMARY KEY,
                cik TEXT NOT NULL,
                field_name TEXT NOT NULL,
                primary_value TEXT NOT NULL,
                secondary_value TEXT NOT NULL,
                source_urls TEXT NOT NULL,
                resolution TEXT NOT NULL,
                rationale TEXT NOT NULL,
                resolver TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS audit_results (
                cik TEXT PRIMARY KEY,
                gross_primary TEXT NOT NULL,
                gross_recompute TEXT NOT NULL,
                delta TEXT NOT NULL,
                passed INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS gate_results (
                run_id TEXT PRIMARY KEY,
                universe_reconciled INTEGER NOT NULL,
                urls_valid INTEGER NOT NULL,
                no_manual_queue INTEGER NOT NULL,
                calc_audit_passed INTEGER NOT NULL,
                no_duplicates INTEGER NOT NULL,
                crosscheck_complete INTEGER NOT NULL,
                verdict TEXT NOT NULL,
                FOREIGN KEY (run_id) REFERENCES runs (run_id)
            );
            """)

    def save_run(self, manifest: RunManifestModel) -> None:
        """Persist Run record."""
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO runs
                (run_id, as_of_date, rule_hash, edgar_user_agent, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    manifest.run_id,
                    str(manifest.as_of_date),
                    manifest.rule_hash,
                    manifest.edgar_user_agent,
                    manifest.status,
                    manifest.created_at,
                ),
            )

    def save_candidates(self, candidates: list[CandidateModel]) -> None:
        """Persist Candidate records."""
        with self._get_connection() as conn:
            conn.executemany(
                """
                INSERT OR REPLACE INTO candidates
                (accession_no, run_id, cik, company_name, form_type, filing_date, classification)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        c.accession_no,
                        c.run_id,
                        c.cik,
                        c.company_name,
                        c.form_type,
                        str(c.filing_date),
                        c.classification,
                    )
                    for c in candidates
                ],
            )

    def save_exclusions(self, exclusions: list[ExclusionModel]) -> None:
        """Persist Exclusion records."""
        with self._get_connection() as conn:
            conn.executemany(
                """
                INSERT OR REPLACE INTO exclusions
                (accession_no, run_id, company_name, reason_code, evidence_url)
                VALUES (?, ?, ?, ?, ?)
                """,
                [
                    (e.accession_no, e.run_id, e.company_name, e.reason_code, e.evidence_url)
                    for e in exclusions
                ],
            )

    def save_ipo_records(self, records: list[IpoRecordModel]) -> None:
        """Persist IPO records."""
        with self._get_connection() as conn:
            conn.executemany(
                """
                INSERT OR REPLACE INTO ipo_records
                (cik, accession_no, company_name, ticker, exchange, pricing_date, offer_price,
                 base_shares, overallotment_shares, gross_offering_amount, form_type,
                 security_type, is_spac, prospectus_url, status, flag_codes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        r.cik,
                        r.accession_no,
                        r.company_name,
                        r.ticker,
                        r.exchange,
                        str(r.pricing_date),
                        str(r.offer_price),
                        r.base_shares,
                        r.overallotment_shares,
                        str(r.gross_offering_amount),
                        r.form_type,
                        r.security_type,
                        1 if r.is_spac else 0,
                        r.prospectus_url,
                        r.status,
                        r.flag_codes,
                    )
                    for r in records
                ],
            )

    def save_evidence(self, evidence: list[EvidenceModel]) -> None:
        """Persist verbatim evidence records."""
        with self._get_connection() as conn:
            conn.executemany(
                """
                INSERT OR REPLACE INTO evidence
                (evidence_id, cik, field_name, value, source_url,
                 doc_sha256, char_offset, snippet, retrieval_timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        ev.evidence_id,
                        ev.cik,
                        ev.field_name,
                        ev.value,
                        ev.source_url,
                        ev.doc_sha256,
                        ev.char_offset,
                        ev.snippet,
                        ev.retrieval_timestamp,
                    )
                    for ev in evidence
                ],
            )

    def save_cross_checks(self, checks: list[CrossCheckModel]) -> None:
        """Persist cross-check records."""
        with self._get_connection() as conn:
            conn.executemany(
                """
                INSERT OR REPLACE INTO cross_checks
                (check_id, cik, source_name, source_url,
                 retrieved_at, values_json, all_fields_match)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        c.check_id,
                        c.cik,
                        c.source_name,
                        c.source_url,
                        c.retrieved_at,
                        c.values_json,
                        1 if c.all_fields_match else 0,
                    )
                    for c in checks
                ],
            )

    def save_discrepancies(self, discrepancies: list[DiscrepancyModel]) -> None:
        """Persist discrepancy records."""
        with self._get_connection() as conn:
            conn.executemany(
                """
                INSERT OR REPLACE INTO discrepancies
                (discrepancy_id, cik, field_name, primary_value, secondary_value, source_urls,
                 resolution, rationale, resolver)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        d.discrepancy_id,
                        d.cik,
                        d.field_name,
                        d.primary_value,
                        d.secondary_value,
                        d.source_urls,
                        d.resolution,
                        d.rationale,
                        d.resolver,
                    )
                    for d in discrepancies
                ],
            )

    def save_audit_results(self, results: list[AuditResultModel]) -> None:
        """Persist calculation audit results."""
        with self._get_connection() as conn:
            conn.executemany(
                """
                INSERT OR REPLACE INTO audit_results
                (cik, gross_primary, gross_recompute, delta, passed)
                VALUES (?, ?, ?, ?, ?)
                """,
                [
                    (
                        a.cik,
                        str(a.gross_primary),
                        str(a.gross_recompute),
                        str(a.delta),
                        1 if a.passed else 0,
                    )
                    for a in results
                ],
            )

    def save_gate_result(self, gate: GateResultModel) -> None:
        """Persist gate result."""
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO gate_results
                (run_id, universe_reconciled, urls_valid, no_manual_queue, calc_audit_passed,
                 no_duplicates, crosscheck_complete, verdict)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    gate.run_id,
                    1 if gate.universe_reconciled else 0,
                    1 if gate.urls_valid else 0,
                    1 if gate.no_manual_queue else 0,
                    1 if gate.calc_audit_passed else 0,
                    1 if gate.no_duplicates else 0,
                    1 if gate.crosscheck_complete else 0,
                    gate.verdict,
                ),
            )
