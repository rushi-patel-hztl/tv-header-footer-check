"""
Polite page pacing for the daily runners (run_daily_compare.py, cloud_run.py).

install(hc, fc) wraps header_compare.extract_header and footer_compare.extract_footer so that:
  - consecutive page loads are spaced by a random MIN_DELAY..MAX_DELAY seconds
  - an HTTP 429 (Too Many Requests) on the page is retried after a back-off
    (Retry-After header if given, otherwise BACKOFF_SECONDS), and reported as an
    error if it is still rate-limited after the last retry

Only the runners call install(); the compare scripts themselves are unchanged.
"""

from __future__ import annotations

import random
import time

MIN_DELAY = 5.0
MAX_DELAY = 10.0
BACKOFF_SECONDS = [60, 120, 240]

_last_load = [0.0]


def _retry_after(headers: dict) -> float:
    try:
        return float(headers.get("retry-after", ""))
    except (TypeError, ValueError):
        return 0.0


def _paced(extract):
    def wrapper(page, url):
        attempts = len(BACKOFF_SECONDS) + 1
        for attempt in range(attempts):
            wait = random.uniform(MIN_DELAY, MAX_DELAY) - (time.monotonic() - _last_load[0])
            if wait > 0:
                time.sleep(wait)

            # Record the main document's HTTP status (including redirects)
            nav: list[tuple[int, dict]] = []

            def on_response(resp):
                try:
                    if resp.request.is_navigation_request() and resp.frame == page.main_frame:
                        nav.append((resp.status, resp.headers))
                except Exception:
                    pass

            page.on("response", on_response)
            try:
                data = extract(page, url)
            finally:
                page.remove_listener("response", on_response)
                _last_load[0] = time.monotonic()

            limited = [h for status, h in nav if status == 429]
            if not limited:
                return data
            if attempt == attempts - 1:
                print(f"  HTTP 429 still returned after {attempts} attempts: {url}")
                data["error"] = "HTTP 429 Too Many Requests (rate limited) - page not checked"
                return data
            backoff = max(BACKOFF_SECONDS[attempt], _retry_after(limited[-1]))
            print(f"  HTTP 429 (rate limited) on {url} - waiting {backoff:.0f}s before retry")
            time.sleep(backoff)
        return data

    return wrapper


def install(hc, fc) -> None:
    """Wrap the header/footer extractors with pacing + 429 back-off."""
    hc.extract_header = _paced(hc.extract_header)
    fc.extract_footer = _paced(fc.extract_footer)
    print(f"Pacing: {MIN_DELAY:.0f}-{MAX_DELAY:.0f}s between page loads; 429 back-off {BACKOFF_SECONDS}s")
