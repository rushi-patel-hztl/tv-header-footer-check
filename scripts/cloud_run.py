"""
Cloud / Linux runner for the daily header + footer check.

Same flow as run_daily_compare.py, but:
  - all paths are relative to the repo root (no c:\\Users\\... paths)
  - Chromium runs headless (no display in the cloud)
  - output is shown on the console as well as written to run.log
  - compares against the CLOUD baseline (baselines/cloud_baseline), kept separate from
    the local baseline because the site varies some content by visitor location

Writes daily/<YYYY-MM-DD_HHMMSS>/ with:
  HeaderCheck_Report.xlsx / .html
  FooterCheck_Report.xlsx / .html
  DifferenceReport.xlsx / .html   (only when something changed vs the cloud baseline)
  run.log
  slack_message.md                (summary posted to Slack by the cloud routine)

Usage (from the repo root):
  python -u scripts/cloud_run.py                  # normal daily run
  python -u scripts/cloud_run.py --set-baseline   # run, then make this run the cloud baseline
  python -u scripts/cloud_run.py --input other.xlsx --out-root /tmp/test   # ad-hoc test
"""

from __future__ import annotations

import argparse
import shutil
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright as _real_sync_playwright

SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parent
sys.path.insert(0, str(SCRIPTS_DIR))

import compare_to_baseline  # noqa: E402
import footer_compare as fc  # noqa: E402
import header_compare as hc  # noqa: E402
import pacing  # noqa: E402

DEFAULT_INPUT = REPO_ROOT / "input" / "DailyCheck.xlsx"
DEFAULT_OUT_ROOT = REPO_ROOT / "daily"
CLOUD_BASELINE_DIR = REPO_ROOT / "baselines" / "cloud_baseline"
REPORT_FILES = [
    "HeaderCheck_Report.xlsx",
    "HeaderCheck_Report.html",
    "FooterCheck_Report.xlsx",
    "FooterCheck_Report.html",
]


class _HeadlessPlaywright:
    """sync_playwright() stand-in that forces chromium.launch(headless=True).

    header_compare / footer_compare launch with headless=False; this avoids editing them.
    """

    def __init__(self):
        self._cm = _real_sync_playwright()

    def __enter__(self):
        p = self._cm.__enter__()
        launch = p.chromium.launch

        def headless_launch(*args, **kwargs):
            kwargs["headless"] = True
            return launch(*args, **kwargs)

        p.chromium.launch = headless_launch
        return p

    def __exit__(self, *exc):
        return self._cm.__exit__(*exc)


class _Tee:
    """Write to both the console and run.log."""

    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for s in self.streams:
            s.write(data)
        return len(data)

    def flush(self):
        for s in self.streams:
            s.flush()


def set_baseline(run_dir: Path) -> None:
    CLOUD_BASELINE_DIR.mkdir(parents=True, exist_ok=True)
    for name in REPORT_FILES:
        shutil.copy2(run_dir / name, CLOUD_BASELINE_DIR / name)
    (CLOUD_BASELINE_DIR / "BASELINE_SOURCE.txt").write_text(
        "Cloud baseline for the daily header/footer check\n"
        f"Copied from: daily/{run_dir.name}\n"
        f"Set at: {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC\n"
        "Do not edit these files - every cloud run is compared against them.\n",
        encoding="utf-8",
    )
    print(f"Cloud baseline set from daily/{run_dir.name} -> {CLOUD_BASELINE_DIR}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Cloud runner for the daily header/footer check")
    ap.add_argument("--input", default=str(DEFAULT_INPUT), help="Source/Target URL pairs (xlsx)")
    ap.add_argument("--out-root", default=str(DEFAULT_OUT_ROOT), help="Folder for run folders")
    ap.add_argument("--set-baseline", action="store_true", help="Make this run the cloud baseline")
    args = ap.parse_args()

    # One folder per run (UTC date + time) so earlier reports are never overwritten
    run_dir = Path(args.out_root) / datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
    run_dir.mkdir(parents=True, exist_ok=False)

    log = open(run_dir / "run.log", "a", encoding="utf-8", buffering=1)
    sys.stdout = sys.stderr = _Tee(sys.__stdout__, log)
    print(f"=== Cloud run started {datetime.now(timezone.utc):%Y-%m-%d %H:%M:%S} UTC ===")
    print(f"Run folder: {run_dir}")

    hc.sync_playwright = fc.sync_playwright = _HeadlessPlaywright
    hc.INPUT_XLSX = fc.INPUT_XLSX = args.input
    hc.OUTPUT_XLSX = str(run_dir / "HeaderCheck_Report.xlsx")
    hc.OUTPUT_HTML = str(run_dir / "HeaderCheck_Report.html")
    fc.OUTPUT_XLSX = str(run_dir / "FooterCheck_Report.xlsx")
    fc.OUTPUT_HTML = str(run_dir / "FooterCheck_Report.html")
    # Space out page loads and back off on HTTP 429
    pacing.install(hc, fc)

    failures = 0
    for name, run in (("HEADER", hc.main), ("FOOTER", fc.main)):
        print(f"\n##### {name} CHECK #####")
        try:
            run()
        except Exception:
            failures += 1
            print(f"{name} CHECK FAILED:")
            traceback.print_exc()

    print("\n##### COMPARE TO CLOUD BASELINE #####")
    if args.set_baseline:
        if failures:
            print("Not setting baseline: the run had failures.")
        else:
            set_baseline(run_dir)
    elif not (CLOUD_BASELINE_DIR / "HeaderCheck_Report.xlsx").exists():
        print("NO CLOUD BASELINE YET - nothing to compare against.")
        print("Run again with --set-baseline (or promote this run) to create one.")
    else:
        try:
            compare_to_baseline.run(run_dir, CLOUD_BASELINE_DIR)
        except Exception:
            failures += 1
            print("BASELINE COMPARE FAILED:")
            traceback.print_exc()

    print(
        f"\n=== Cloud run finished {datetime.now(timezone.utc):%Y-%m-%d %H:%M:%S} UTC "
        f"(failures={failures}) ==="
    )
    # Email the result of every run (best effort: a mail problem never fails the run)
    try:
        import subprocess
        r = subprocess.run(
            [sys.executable, str(Path(__file__).with_name("send_email.py")), "--run-dir", str(run_dir)],
            capture_output=True, text=True, timeout=120,
        )
        print("EMAIL:", (r.stdout or r.stderr).strip()[-300:])
    except Exception as e:
        print(f"EMAIL FAILED: {e}")
    # Slack summary for the routine to post (best effort, like the email)
    try:
        r = subprocess.run(
            [sys.executable, str(Path(__file__).with_name("slack_summary.py")), "--run-dir", str(run_dir)],
            capture_output=True, text=True, timeout=120,
        )
        print("SLACK SUMMARY:", "written to slack_message.md" if r.returncode == 0 else r.stderr.strip()[-300:])
    except Exception as e:
        print(f"SLACK SUMMARY FAILED: {e}")

    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
    log.close()
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
