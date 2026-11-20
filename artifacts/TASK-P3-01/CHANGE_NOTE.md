# Change Note - TASK-P3-01

## What Changed
- Implemented `EdgarClient` with rate-limiting (<= 5 req/sec), custom `User-Agent`, content-addressed caching, and document retrieval.
- Implemented secondary source adapters:
  - `src/ipo_ledger/adapters/secondary/nasdaq.py` (`NasdaqCalendarAdapter`)
  - `src/ipo_ledger/adapters/secondary/provider.py` (`FinancialProviderAdapter`)
- Added unit tests in `tests/unit/test_secondary_adapters.py`.

## What Could Break
- Network timeouts or rate limits from SEC EDGAR are handled with retry intervals; persistent network outage will trigger typed exceptions.
