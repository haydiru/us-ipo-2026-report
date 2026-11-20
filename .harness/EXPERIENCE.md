# Institutional Experience Log

This document records institutional memory of failures, root cause analyses, and verified fixes across pipeline stages.

## Experience Records

### Entry 001 - Invariant Rules Setup
- **Context / Stack:** Initial harness setup and environment validation.
- **Root Cause of Failure:** Potential drift in gross calculation, greenshoe inclusion, or naive datetime access.
- **Verified Harness Fix:** Injected deterministic Clock protocol; Decimal arithmetic with integer recompute; isolated pure domain layer enforced via import-linter.
- **Enforcement Level:** Type / Lint / Architecture Boundary.
