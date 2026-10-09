# TeamViewer header / footer daily check

Compares the header and footer (links, visible text labels, `target="_blank"`) of two pages per locale and
reports any change against a fixed baseline.

| | Page | CMS |
|---|---|---|
| Source | `https://www.teamviewer.com/<locale>/` (home page) | AEM |
| Target | `https://www.teamviewer.com/<locale>/global/company/press/2026/teamviewer-expands-ai-powered-it-troubleshooting-from-guidance-to-governed-action/` | Sitecore |

17 locales: en, de, fr, es, ja, pt, cn, hu, it, ko, nl, pl, th, ru, cs, tw, tr (see `input/DailyCheck.xlsx`).

## Layout

| Path | Contents |
|---|---|
| `scripts/header_compare.py` | Header extraction (Playwright) + matching / scoring + Excel report |
| `scripts/footer_compare.py` | Footer extraction, reusing the header matching with footer-specific rules |
| `scripts/generate_html_report.py` | HTML version of an Excel report |
| `scripts/run_daily_compare.py` | Daily runner: header check, footer check, then compare to baseline |
| `scripts/compare_to_baseline.py` | Diffs a run against the baseline; writes `DifferenceReport.*` only when something changed |
| `input/DailyCheck.xlsx` | Source / Target URL pairs |
| `baselines/daily_baseline/` | Baseline reports (run of 2026-10-09 17:55, 17 locales) |
| `daily/<YYYY-MM-DD_HHMMSS>/` | One folder per run |

## Reading a run folder

- `HeaderCheck_Report.*`, `FooterCheck_Report.*` — the page1 vs page2 comparison for that run.
- `DifferenceReport.*` — **present only if something changed vs the baseline** (any match % change, status change,
  or a link / text added, removed or renamed on either page). No file = no change.
- `run.log` — full run output.

`daily/2026-10-09` is an earlier EN-only run; `daily/2026-10-09_175543` is the 17-locale run used as the baseline.

## Running in the cloud / on Linux

```bash
./setup.sh                                   # pip packages + headless Chromium
python3 -u scripts/cloud_run.py              # daily run, compared to baselines/cloud_baseline
python3 -u scripts/cloud_run.py --set-baseline   # run once and make it the cloud baseline
```

`cloud_run.py` uses repo-relative paths, forces headless Chromium and writes `daily/<UTC date_time>/`.
It compares against `baselines/cloud_baseline/`, kept separate from the local baseline
(`baselines/daily_baseline/`) because the site varies some content (e.g. phone numbers) by visitor location.

## Running locally (Windows)

`scripts/run_daily_compare.py` is the local runner. It uses the local paths it was written with
(`c:\Users\rpatel\...`) and a visible browser, and compares against `baselines/daily_baseline/`.
