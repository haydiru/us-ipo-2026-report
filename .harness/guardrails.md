# Project Guardrails & Invariants

## Strict Negative Constraints
1. **Never use float arithmetic for money or prices:** All calculations must use Python `Decimal` or integer units (`1e4`).
2. **Never include over-allotment (greenshoe) in base shares:** Base shares must strictly capture initial offering shares. Greenshoe is recorded separately.
3. **Never guess or fabricate missing data:** If a value cannot be authoritatively extracted or verified from primary filings, leave it blank and flag the record.
4. **Never bypass SEC rate limiting or fair access:** Always include a descriptive `User-Agent` header and respect rate limits (<= 5 req/sec).
5. **Domain purity:** `ipo_ledger.domain` must have zero external I/O, no network calls, no database access, and no naive clock access.
