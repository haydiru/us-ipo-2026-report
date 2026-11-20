"""Completeness Gate evaluation logic (PRD Section 3.8)."""

from typing import Literal

from ipo_ledger.domain.schema import GateResultModel


def evaluate_gate(
    run_id: str,
    universe_reconciled: bool,
    urls_valid: bool,
    manual_queue_empty: bool,
    calc_audit_passed: bool,
    no_duplicates: bool,
    crosscheck_complete: bool,
    unmatched_calendar_reasons: list[str] | None = None,
) -> GateResultModel:
    """Evaluate the six mandatory completeness conditions and determine verdict."""
    blockers: list[str] = []

    if not universe_reconciled:
        blockers.append("Exchange calendar reconciliation failed or has unexplained missing IPOs.")

    if not urls_valid:
        blockers.append("One or more prospectus URLs did not return HTTP 200 on Form 424B4/424B1.")

    if not manual_queue_empty:
        blockers.append("Manual review queue is not empty; unresolved records remain.")

    if not calc_audit_passed:
        blockers.append("Independent recompute audit failed on one or more records.")

    if not no_duplicates:
        blockers.append("Duplicate CIK or ticker-date records detected.")

    if not crosscheck_complete:
        blockers.append(
            "Records remain unverified without valid secondary source or SINGLE_SOURCE flag."
        )

    all_passed = (
        universe_reconciled
        and urls_valid
        and manual_queue_empty
        and calc_audit_passed
        and no_duplicates
        and crosscheck_complete
    )

    verdict: Literal["VERIFIED", "DRAFT_INCOMPLETE"] = (
        "VERIFIED" if all_passed else "DRAFT_INCOMPLETE"
    )

    return GateResultModel(
        run_id=run_id,
        universe_reconciled=universe_reconciled,
        urls_valid=urls_valid,
        no_manual_queue=manual_queue_empty,
        calc_audit_passed=calc_audit_passed,
        no_duplicates=no_duplicates,
        crosscheck_complete=crosscheck_complete,
        verdict=verdict,
        blockers=blockers,
    )
