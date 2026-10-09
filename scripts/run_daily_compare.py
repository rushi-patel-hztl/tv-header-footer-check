"""
Nightly page1 vs page2 run: header_compare + footer_compare.

Reads Source/Target pairs from DailyCheck.xlsx.
Writes each run to its own date + time folder so reports are not overwritten:
  c:\\Users\\rpatel\\Desktop\\Teamviewer\\daily\\<YYYY-MM-DD_HHMMSS>\\
    HeaderCheck_Report.xlsx / .html
    FooterCheck_Report.xlsx / .html
    DifferenceReport.xlsx / .html   (only when something changed vs baseline)
    run.log

Baseline: c:\\Users\\rpatel\\Desktop\\Teamviewer\\baselines\\daily_baseline (see compare_to_baseline.py)

Scheduled via a Claude desktop scheduled task ("TeamViewer header/footer daily check").
"""

from __future__ import annotations

import sys
import traceback
from datetime import datetime
from pathlib import Path

import compare_to_baseline
import footer_compare as fc
import header_compare as hc

DAILY_ROOT = Path(r"c:\Users\rpatel\Desktop\Teamviewer\daily")
# Source/Target pairs for the nightly run (same layout as HeaderCheck.xlsx)
DAILY_INPUT_XLSX = r"c:\Users\rpatel\Desktop\Teamviewer\DailyCheck.xlsx"


def main() -> int:
    # One folder per run (date + time) so earlier reports are never overwritten
    run_dir = DAILY_ROOT / datetime.now().strftime("%Y-%m-%d_%H%M%S")
    run_dir.mkdir(parents=True, exist_ok=False)

    # pythonw has no console — send all output to the run log
    log = open(run_dir / "run.log", "a", encoding="utf-8", buffering=1)
    sys.stdout = sys.stderr = log
    print(f"=== Daily run started {datetime.now():%Y-%m-%d %H:%M:%S} ===")

    # Point each script's input / output constants at the daily files
    hc.INPUT_XLSX = fc.INPUT_XLSX = DAILY_INPUT_XLSX
    hc.OUTPUT_XLSX = str(run_dir / "HeaderCheck_Report.xlsx")
    hc.OUTPUT_HTML = str(run_dir / "HeaderCheck_Report.html")
    fc.OUTPUT_XLSX = str(run_dir / "FooterCheck_Report.xlsx")
    fc.OUTPUT_HTML = str(run_dir / "FooterCheck_Report.html")

    failures = 0
    for name, run in (("HEADER", hc.main), ("FOOTER", fc.main)):
        print(f"\n##### {name} CHECK #####")
        try:
            run()
        except Exception:
            failures += 1
            print(f"{name} CHECK FAILED:")
            traceback.print_exc()

    # Compare against the fixed baseline; writes DifferenceReport.* only if something changed
    print("\n##### COMPARE TO BASELINE #####")
    try:
        compare_to_baseline.run(run_dir)
    except Exception:
        failures += 1
        print("BASELINE COMPARE FAILED:")
        traceback.print_exc()

    print(f"\n=== Daily run finished {datetime.now():%Y-%m-%d %H:%M:%S} (failures={failures}) ===")
    log.close()
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
