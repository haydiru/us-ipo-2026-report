# Multi-Agent & Anti-AI-Slop Engineering Workflow Summary

Rather than relying on single-prompt web searches—which inevitably produce "AI slop" (hallucinated numbers, greenshoe mix-ups, and broken links)—this solution was engineered using a **custom Harness-Driven PRD Architecture** paired with a **Two-Agent Execution & Independent Audit Loop**.

---

### Phase 1: Custom Anti-AI-Slop PRD & Deterministic Harness Design
Before writing any extraction code, I designed a strict, reusable **Harness Engineering PRD** to constrain LLM behavior and enforce deterministic data integrity:
- **Separation of Concerns (LLM vs. Deterministic Code):** LLMs were strictly banned from performing arithmetic, web-search guessing, or direct spreadsheet writing. All EDGAR API discovery, rate-limiting, SHA-256 document caching, and `Decimal` / integer micro-dollar calculations were enforced in pure, strictly typed Python (`mypy --strict` + Pydantic frozen schemas).
- **Custom Guardrails & Linter Enforcement:** Built project-specific AST lint rules and invariants (`IPO001`–`IPO009`) to programmatically block float money, separate underwriter over-allotment (*greenshoe*) options from base shares, and reject any LLM-extracted figure that failed a **verbatim string-presence check** against the cached SEC filing.
- **Mechanical Completeness Gate (`Stage S6`):** Configured an automated gate that refuses to mark a dataset `VERIFIED` if unresolved discrepancies, duplicate CIKs, or broken SEC URLs exist.

### Phase 2: Pipeline Execution (Agent 1 — Antigravity)
- Executed the PRD across the 2026 SEC EDGAR Form 424B4 index (Jan 1 – Nov 20, 2026), caching raw prospectuses locally and generating an initial 283-row workbook (`$240.1B` gross).

### Phase 3: Independent Second-Layer Audit & Patching (Agent 2 — Claude Code)
Because an AI agent should never be the sole grader of its own output, I deployed an independent auditor agent (Claude Code) to verify the Pass-1 workbook directly against the cached SEC 424B4 cover pages:
- **Uncovered Hidden Pass-1 Defects (~100 rows):** Caught ~40 fallback placeholder values (`$20.00` / `10,000,000` shares), follow-on filing mix-ups (`FPS`, `MANE`), greenshoe contamination (`BRKH`), T+1 filing dates used as pricing dates (119 rows), and scope leaks (11 NYSE American listings, 18 direct listings/resales).
- **Deterministic Patching & Live SEC Verification (`scripts/audit_verify_final.py`):** Re-derived base shares directly from cover-page tables (`cover total ÷ offer price`), executed a live SEC EDGAR API verification for two uncached tickers (`BRAI`, `WSHP` — confirmed as resale registrations and excluded), verified **241/241 live Excel formulas (`=E*F`)**, and emitted the final audited deliverable (`us_ipo_report_2026.xlsx`) alongside `AUDIT_REPORT.md`.