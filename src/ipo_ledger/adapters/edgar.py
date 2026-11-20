"""SEC EDGAR URL builder and rate-limited client adapter (PRD Section 2.3, 8.3)."""

import time

import httpx

from ipo_ledger.adapters.cache import ContentCache


class EdgarUrls:
    """Centralized URL construction for SEC EDGAR filings and submissions."""

    BASE_URL = "https://www.sec.gov"
    DATA_URL = "https://data.sec.gov"

    @classmethod
    def form_index_url(cls, year: int, quarter: str) -> str:
        """Construct full form index URL for quarter."""
        return f"{cls.BASE_URL}/Archives/edgar/full-index/{year}/{quarter}/form.idx"

    @classmethod
    def daily_form_index_url(cls, year: int, quarter: str, date_str: str) -> str:
        """Construct daily form index URL."""
        return f"{cls.BASE_URL}/Archives/edgar/daily-index/{year}/{quarter}/form.{date_str}.idx"

    @classmethod
    def submissions_url(cls, cik: str) -> str:
        """Construct submissions JSON URL for zero-padded CIK."""
        padded_cik = cik.zfill(10)
        return f"{cls.DATA_URL}/submissions/CIK{padded_cik}.json"

    @classmethod
    def accession_document_url(cls, cik: str, accession_no: str, document_name: str) -> str:
        """Construct authoritative filing document URL."""
        clean_acc = accession_no.replace("-", "")
        clean_cik = str(int(cik))
        return f"{cls.BASE_URL}/Archives/edgar/data/{clean_cik}/{clean_acc}/{document_name}"

    @classmethod
    def fallback_filing_url(cls, accession_no: str) -> str:
        """Fallback accession URL."""
        return f"{cls.BASE_URL}/edgar/search/#/accession={accession_no}"


class EdgarClient:
    """Rate-limited, cached SEC EDGAR HTTP client."""

    def __init__(self, user_agent: str, cache: ContentCache, timeout_seconds: float = 20.0) -> None:
        self.user_agent = user_agent
        self.cache = cache
        self.timeout_seconds = timeout_seconds
        self._last_request_time = 0.0
        self._min_interval = 0.25

    def _enforce_rate_limit(self) -> None:
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)
        self._last_request_time = time.time()

    def fetch_url(self, url: str) -> tuple[int, bytes, str]:
        """Fetch URL content respecting caching and fair access."""
        self._enforce_rate_limit()
        headers = {
            "User-Agent": self.user_agent,
            "Accept-Encoding": "gzip, deflate",
        }
        with httpx.Client(timeout=self.timeout_seconds, follow_redirects=True) as client:
            resp = client.get(url, headers=headers)
            content = resp.content
            sha, _ = self.cache.put(content)
            return resp.status_code, content, sha

    def get_form_index(self, year: int, quarter: str) -> str:
        """Fetch quarterly form index text."""
        url = EdgarUrls.form_index_url(year, quarter)
        status, content, _ = self.fetch_url(url)
        if status != 200:
            raise RuntimeError(f"Failed to fetch form index for {year} {quarter}: HTTP {status}")
        return content.decode("utf-8", errors="replace")

    def get_filing_document(self, url: str) -> tuple[int, str, str]:
        """Fetch primary prospectus text and content hash."""
        status, content, sha = self.fetch_url(url)
        text = content.decode("utf-8", errors="replace")
        return status, text, sha
