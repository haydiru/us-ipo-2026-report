"""Stage S3: Cross-Verification against secondary sources (PRD Section 3.4)."""

import json
from pathlib import Path

from ipo_ledger.adapters.storage import LedgerStorage
from ipo_ledger.domain.reconcile import SecondaryCheckValues, reconcile_record
from ipo_ledger.domain.schema import CrossCheckModel, DiscrepancyModel, IpoRecordModel


class StageS3CrossCheck:
    """Stage S3 orchestrator for multi-source verification and discrepancy logging."""

    def __init__(self, storage: LedgerStorage) -> None:
        self.storage = storage

    def run(
        self,
        records: list[IpoRecordModel],
        secondary_map: dict[str, list[SecondaryCheckValues]],
        output_dir: Path,
    ) -> tuple[list[IpoRecordModel], list[CrossCheckModel], list[DiscrepancyModel]]:
        """Execute cross-check comparisons, resolve discrepancies, and persist outputs."""
        output_dir.mkdir(parents=True, exist_ok=True)
        updated_records: list[IpoRecordModel] = []
        cross_checks: list[CrossCheckModel] = []
        all_discrepancies: list[DiscrepancyModel] = []

        check_id = 1
        disc_id = 1

        for rec in records:
            sec_list = secondary_map.get(rec.cik, [])

            for sec in sec_list:
                matches_all = (
                    (sec.offer_price is None or sec.offer_price == rec.offer_price)
                    and (sec.base_shares is None or sec.base_shares == rec.base_shares)
                    and (sec.pricing_date is None or sec.pricing_date == rec.pricing_date)
                    and (not sec.ticker or sec.ticker.upper() == rec.ticker.upper())
                )
                values_dict = {
                    "ticker": sec.ticker,
                    "exchange": sec.exchange,
                    "pricing_date": str(sec.pricing_date) if sec.pricing_date else None,
                    "offer_price": str(sec.offer_price) if sec.offer_price else None,
                    "base_shares": sec.base_shares,
                }
                cross_checks.append(
                    CrossCheckModel(
                        check_id=check_id,
                        cik=rec.cik,
                        source_name=sec.source_name,
                        source_url=sec.source_url,
                        retrieved_at="2026-11-20T12:00:00Z",
                        values_json=json.dumps(values_dict),
                        all_fields_match=matches_all,
                    )
                )
                check_id += 1

            new_status, flag_list, record_discrepancies = reconcile_record(
                cik=rec.cik,
                primary_ticker=rec.ticker,
                primary_exchange=rec.exchange,
                primary_pricing_date=rec.pricing_date,
                primary_offer_price=rec.offer_price,
                primary_base_shares=rec.base_shares,
                secondary_checks=sec_list,
                prospectus_url=rec.prospectus_url,
                discrepancy_id_start=disc_id,
            )
            disc_id += len(record_discrepancies)
            all_discrepancies.extend(record_discrepancies)

            combined_flags = ";".join(flag_list)
            updated_rec = IpoRecordModel(
                cik=rec.cik,
                accession_no=rec.accession_no,
                company_name=rec.company_name,
                ticker=rec.ticker,
                exchange=rec.exchange,
                pricing_date=rec.pricing_date,
                offer_price=rec.offer_price,
                base_shares=rec.base_shares,
                overallotment_shares=rec.overallotment_shares,
                gross_offering_amount=rec.gross_offering_amount,
                form_type=rec.form_type,
                security_type=rec.security_type,
                is_spac=rec.is_spac,
                prospectus_url=rec.prospectus_url,
                status=new_status,  # type: ignore[arg-type]
                flag_codes=combined_flags,
            )
            updated_records.append(updated_rec)

        self.storage.save_cross_checks(cross_checks)
        self.storage.save_discrepancies(all_discrepancies)
        self.storage.save_ipo_records(updated_records)

        cc_path = output_dir / "cross_checks.json"
        cc_path.write_text(
            json.dumps([c.model_dump(mode="json") for c in cross_checks], indent=2),
            encoding="utf-8",
        )

        disc_path = output_dir / "discrepancies.json"
        disc_path.write_text(
            json.dumps([d.model_dump(mode="json") for d in all_discrepancies], indent=2),
            encoding="utf-8",
        )

        return updated_records, cross_checks, all_discrepancies
