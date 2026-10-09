"""
Generate an interactive HTML report from HeaderCheck_Report.xlsx
showing matched, renamed, missing, and additional header links/texts.
"""

from __future__ import annotations

import html
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from openpyxl import load_workbook

INPUT_XLSX = r"c:\Users\rpatel\Desktop\Teamviewer\HeaderCheck_Report_v7.xlsx"
OUTPUT_HTML = r"c:\Users\rpatel\Desktop\Teamviewer\HeaderCheck_Report_v7.html"


def esc(value) -> str:
    if value is None:
        return ""
    return html.escape(str(value))


def rows_as_dicts(ws) -> list[dict]:
    headers = [c.value for c in ws[1]]
    out = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if all(v is None for v in row):
            continue
        out.append({headers[i]: row[i] for i in range(len(headers))})
    return out


def status_class(status: str) -> str:
    s = (status or "").upper()
    if s == "PASS":
        return "pass"
    if s == "WARN":
        return "warn"
    if s == "ERROR":
        return "error"
    return "fail"


def pct_bar(pct) -> str:
    try:
        p = float(pct or 0)
    except (TypeError, ValueError):
        p = 0.0
    p = max(0.0, min(100.0, p))
    if p >= 95:
        color = "var(--pass)"
    elif p >= 80:
        color = "var(--warn)"
    else:
        color = "var(--fail)"
    return (
        f'<div class="bar"><span style="width:{p:.1f}%;background:{color}"></span>'
        f'<em>{p:.1f}%</em></div>'
    )


def group_by_locale(rows: list[dict], key="Locale") -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        locale = r.get(key) or "?"
        grouped[str(locale)].append(r)
    return grouped


def render_link_table(rows: list[dict], columns: list[tuple[str, str]], empty_msg: str) -> str:
    if not rows:
        return f'<p class="empty">{esc(empty_msg)}</p>'
    thead = "".join(f"<th>{esc(label)}</th>" for _, label in columns)
    body = []
    for r in rows:
        tds = "".join(f"<td>{esc(r.get(key))}</td>" for key, _ in columns)
        body.append(f"<tr>{tds}</tr>")
    return (
        f'<div class="table-wrap"><table><thead><tr>{thead}</tr></thead>'
        f'<tbody>{"".join(body)}</tbody></table></div>'
    )


def render_chip_list(items: list[str], css: str) -> str:
    if not items:
        return '<p class="empty">None</p>'
    chips = "".join(f'<span class="chip {css}">{esc(t)}</span>' for t in items)
    return f'<div class="chips">{chips}</div>'


def build_html(data: dict, component: str = "Header", mode: str = "cross_env") -> str:
    summary = data["summary"]
    matching_links = group_by_locale(data["matching_links"])
    renamed_links = group_by_locale(data["renamed_links"])
    missing_links = group_by_locale(data["missing_links"])
    additional_links = group_by_locale(data["additional_links"])
    matching_texts = group_by_locale(data["matching_texts"])
    missing_texts = group_by_locale(data["missing_texts"])
    additional_texts = group_by_locale(data["additional_texts"])
    blank_mismatches = group_by_locale(data.get("blank_mismatches") or [])
    component = component or "Header"

    total = len(summary)
    pass_n = sum(1 for r in summary if (r.get("Status") or "").upper() == "PASS")
    warn_n = sum(1 for r in summary if (r.get("Status") or "").upper() == "WARN")
    fail_n = sum(1 for r in summary if (r.get("Status") or "").upper() == "FAIL")
    error_n = sum(1 for r in summary if (r.get("Status") or "").upper() == "ERROR")

    avg_overall = (
        sum(float(r.get("Overall Match %") or 0) for r in summary) / total if total else 0
    )
    avg_struct = (
        sum(float(r.get("Structural Link Match %") or 0) for r in summary) / total if total else 0
    )

    summary_rows = []
    for r in summary:
        locale = esc(r.get("Locale"))
        status = esc(r.get("Status"))
        sc = status_class(r.get("Status"))
        summary_rows.append(
            f"""
            <tr class="{sc}">
              <td><a href="#locale-{locale}">{locale}</a></td>
              <td>{pct_bar(r.get("Overall Match %"))}</td>
              <td>{pct_bar(r.get("Structural Link Match %"))}</td>
              <td>{pct_bar(r.get("Exact Link Match %"))}</td>
              <td>{pct_bar(r.get("Text Match %"))}</td>
              <td class="num ok">{esc(r.get("Exact Matching Links"))}</td>
              <td class="num warn">{esc(r.get("Renamed Slug Links"))}</td>
              <td class="num fail">{esc(r.get("Truly Missing in Target"))}</td>
              <td class="num add">{esc(r.get("Truly Additional in Target"))}</td>
              <td class="num fail">{esc(r.get("target=_blank Mismatches"))}</td>
              <td><span class="badge {sc}">{status}</span></td>
            </tr>
            """
        )

    locale_sections = []
    for r in summary:
        locale = str(r.get("Locale") or "?")
        sc = status_class(r.get("Status"))
        m_links = matching_links.get(locale, [])
        r_links = renamed_links.get(locale, [])
        miss = missing_links.get(locale, [])
        add = additional_links.get(locale, [])
        blanks = blank_mismatches.get(locale, [])
        m_texts = [x.get("Matching Text Label") for x in matching_texts.get(locale, [])]
        miss_texts = [x.get("Missing Text (in Source only)") for x in missing_texts.get(locale, [])]
        add_texts = [x.get("Additional Text (in Target only)") for x in additional_texts.get(locale, [])]

        locale_sections.append(
            f"""
            <section class="locale-card" id="locale-{esc(locale)}">
              <header class="locale-head">
                <div>
                  <h2><span class="locale-code">{esc(locale)}</span> {esc(component)} Comparison</h2>
                  <p class="urls">
                    <a href="{esc(r.get("Source URL"))}" target="_blank" rel="noopener">Source</a>
                    <span>→</span>
                    <a href="{esc(r.get("Target URL"))}" target="_blank" rel="noopener">Target</a>
                  </p>
                </div>
                <div class="locale-stats">
                  <span class="badge {sc}">{esc(r.get("Status"))}</span>
                  <div class="mini-metric"><label>Overall</label>{pct_bar(r.get("Overall Match %"))}</div>
                  <div class="mini-metric"><label>Structural Links</label>{pct_bar(r.get("Structural Link Match %"))}</div>
                  <div class="mini-metric"><label>Exact Paths</label>{pct_bar(r.get("Exact Link Match %"))}</div>
                  <div class="mini-metric"><label>Texts</label>{pct_bar(r.get("Text Match %"))}</div>
                </div>
              </header>

              <div class="stat-grid">
                <div class="stat ok"><strong>{len(m_links)}</strong><span>Exact matching links</span></div>
                <div class="stat warn"><strong>{len(r_links)}</strong><span>Renamed slug links</span></div>
                <div class="stat fail"><strong>{len(miss)}</strong><span>Missing in target</span></div>
                <div class="stat add"><strong>{len(add)}</strong><span>Additional in target</span></div>
                <div class="stat fail"><strong>{len(blanks)}</strong><span>target=_blank mismatches</span></div>
                <div class="stat ok"><strong>{len(m_texts)}</strong><span>Matching texts</span></div>
                <div class="stat fail"><strong>{len(miss_texts)}</strong><span>Missing texts</span></div>
                <div class="stat add"><strong>{len(add_texts)}</strong><span>Additional texts</span></div>
              </div>

              <details open class="block fail-block">
                <summary>target=_blank Mismatches <em>{len(blanks)}</em></summary>
                {render_link_table(
                    blanks,
                    [
                        ("Issue", "Issue"),
                        ("Structural Key", "Structural Key"),
                        ("Link Text", "Link Text"),
                        ("Source target attr", "Source target"),
                        ("Target target attr", "Target target"),
                        ("Source Href", "Source Href"),
                        ("Target Href", "Target Href"),
                    ],
                    "No target=_blank mismatches on paired links.",
                )}
              </details>

              <details open class="block fail-block">
                <summary>Missing in Target <em>{len(miss)}</em></summary>
                {render_link_table(
                    miss,
                    [
                        ("Exact Path", "Exact Path"),
                        ("Structural Key", "Structural Key"),
                        ("Link Text", "Link Text"),
                        ("Source Href", "Source Href"),
                    ],
                    "No truly missing links — all source links found on target (structurally).",
                )}
              </details>

              <details open class="block add-block">
                <summary>Additional in Target <em>{len(add)}</em></summary>
                {render_link_table(
                    add,
                    [
                        ("Exact Path", "Exact Path"),
                        ("Structural Key", "Structural Key"),
                        ("Link Text", "Link Text"),
                        ("Target Href", "Target Href"),
                    ],
                    "No additional links on target.",
                )}
              </details>

              <details class="block warn-block">
                <summary>Renamed Slug Links <em>{len(r_links)}</em></summary>
                {render_link_table(
                    r_links,
                    [
                        ("Source Exact Path", "Source Path"),
                        ("Target Exact Path", "Target Path"),
                        ("Source Text", "Source Text"),
                        ("Target Text", "Target Text"),
                    ],
                    "No renamed slug links.",
                )}
              </details>

              <details class="block ok-block">
                <summary>Exact Matching Links <em>{len(m_links)}</em></summary>
                {render_link_table(
                    m_links,
                    [
                        ("Exact Path", "Path"),
                        ("Source Text", "Source Text"),
                        ("Target Text", "Target Text"),
                        ("Text Match", "Text Match"),
                        ("Source Href", "Source Href"),
                        ("Target Href", "Target Href"),
                    ],
                    "No exact matching links.",
                )}
              </details>

              <details class="block text-block">
                <summary>Text Labels
                  <em class="ok">{len(m_texts)} matched</em>
                  <em class="fail">{len(miss_texts)} missing</em>
                  <em class="add">{len(add_texts)} additional</em>
                </summary>
                <div class="text-cols">
                  <div>
                    <h3 class="ok">Matched</h3>
                    {render_chip_list([t for t in m_texts if t], "ok")}
                  </div>
                  <div>
                    <h3 class="fail">Missing on Target</h3>
                    {render_chip_list([t for t in miss_texts if t], "fail")}
                  </div>
                  <div>
                    <h3 class="add">Additional on Target</h3>
                    {render_chip_list([t for t in add_texts if t], "add")}
                  </div>
                </div>
              </details>
            </section>
            """
        )

    generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rules = (
        "visible text only; ignores aria-labels &amp; .utils-visually-hidden; "
        "ru-cis≡ru; includes target=_blank checks"
    )
    if mode == "baseline":
        subtitle = (
            f"Baseline (pre-deploy snapshot) vs Live (same URL after deploy) — "
            f"domain must not change; link hosts are compared; {rules} — "
            f"generated {esc(generated)}"
        )
        title_suffix = "Baseline"
    else:
        subtitle = (
            f"Source (www.teamviewer.com) vs Target (prod-sitecore.teamviewer.com) — "
            f"{rules} — generated {esc(generated)}"
        )
        title_suffix = "Check"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{esc(component)} {title_suffix} Report — TeamViewer</title>
<style>
  :root {{
    --bg: #0f1419;
    --panel: #171d25;
    --panel-2: #1e2630;
    --border: #2c3642;
    --text: #e7edf5;
    --muted: #93a0b0;
    --pass: #22c55e;
    --warn: #f59e0b;
    --fail: #ef4444;
    --add: #38bdf8;
    --error: #a855f7;
    --link: #7dd3fc;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    background: radial-gradient(1200px 600px at 10% -10%, #1a2740 0%, transparent 50%),
                radial-gradient(900px 500px at 100% 0%, #1b2a22 0%, transparent 45%),
                var(--bg);
    color: var(--text);
    line-height: 1.45;
  }}
  a {{ color: var(--link); text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  .wrap {{ max-width: 1280px; margin: 0 auto; padding: 28px 20px 60px; }}
  header.hero {{
    display: flex; flex-wrap: wrap; gap: 20px; justify-content: space-between;
    align-items: flex-end; margin-bottom: 24px;
  }}
  header.hero h1 {{ margin: 0 0 6px; font-size: 1.8rem; letter-spacing: -0.02em; }}
  header.hero p {{ margin: 0; color: var(--muted); }}
  .kpis {{ display: flex; gap: 10px; flex-wrap: wrap; }}
  .kpi {{
    background: var(--panel); border: 1px solid var(--border); border-radius: 12px;
    padding: 12px 14px; min-width: 110px;
  }}
  .kpi strong {{ display: block; font-size: 1.35rem; }}
  .kpi span {{ color: var(--muted); font-size: 0.8rem; }}
  .filters {{
    display: flex; gap: 10px; flex-wrap: wrap; align-items: center;
    margin: 0 0 18px; padding: 12px; background: var(--panel);
    border: 1px solid var(--border); border-radius: 12px;
  }}
  .filters input, .filters select {{
    background: var(--panel-2); color: var(--text); border: 1px solid var(--border);
    border-radius: 8px; padding: 8px 10px; font: inherit;
  }}
  .filters input {{ flex: 1; min-width: 220px; }}
  .legend {{ display: flex; gap: 12px; flex-wrap: wrap; color: var(--muted); font-size: 0.85rem; }}
  .legend i {{
    display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 5px;
  }}
  .panel {{
    background: var(--panel); border: 1px solid var(--border); border-radius: 14px;
    padding: 14px; margin-bottom: 22px; overflow: auto;
  }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.9rem; }}
  th, td {{ padding: 10px 8px; border-bottom: 1px solid var(--border); text-align: left; vertical-align: top; }}
  th {{ color: var(--muted); font-weight: 600; position: sticky; top: 0; background: var(--panel); }}
  tr.fail td:first-child, tr.warn td:first-child, tr.pass td:first-child, tr.error td:first-child {{
    border-left: 3px solid transparent;
  }}
  tr.fail td:first-child {{ border-left-color: var(--fail); }}
  tr.warn td:first-child {{ border-left-color: var(--warn); }}
  tr.pass td:first-child {{ border-left-color: var(--pass); }}
  tr.error td:first-child {{ border-left-color: var(--error); }}
  .num {{ text-align: center; font-variant-numeric: tabular-nums; }}
  .num.ok {{ color: var(--pass); }}
  .num.warn {{ color: var(--warn); }}
  .num.fail {{ color: var(--fail); }}
  .num.add {{ color: var(--add); }}
  .badge {{
    display: inline-block; padding: 3px 9px; border-radius: 999px; font-size: 0.75rem;
    font-weight: 700; letter-spacing: 0.04em;
  }}
  .badge.pass {{ background: rgba(34,197,94,.15); color: var(--pass); }}
  .badge.warn {{ background: rgba(245,158,11,.15); color: var(--warn); }}
  .badge.fail {{ background: rgba(239,68,68,.15); color: var(--fail); }}
  .badge.error {{ background: rgba(168,85,247,.15); color: var(--error); }}
  .bar {{
    position: relative; height: 18px; background: #243041; border-radius: 999px;
    overflow: hidden; min-width: 90px;
  }}
  .bar span {{ display: block; height: 100%; border-radius: 999px; }}
  .bar em {{
    position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
    font-style: normal; font-size: 0.72rem; font-weight: 700; color: #fff;
    text-shadow: 0 1px 2px rgba(0,0,0,.55);
  }}
  .locale-card {{
    background: var(--panel); border: 1px solid var(--border); border-radius: 16px;
    padding: 18px; margin-bottom: 18px;
  }}
  .locale-head {{
    display: flex; flex-wrap: wrap; gap: 16px; justify-content: space-between;
    align-items: flex-start; margin-bottom: 14px;
  }}
  .locale-head h2 {{ margin: 0 0 6px; font-size: 1.25rem; }}
  .locale-code {{
    display: inline-block; background: var(--panel-2); border: 1px solid var(--border);
    border-radius: 8px; padding: 2px 8px; margin-right: 6px; text-transform: uppercase;
  }}
  .urls {{ display: flex; gap: 8px; align-items: center; color: var(--muted); flex-wrap: wrap; }}
  .locale-stats {{ display: grid; gap: 8px; min-width: 260px; }}
  .mini-metric label {{ display: block; color: var(--muted); font-size: 0.75rem; margin-bottom: 3px; }}
  .stat-grid {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 8px; margin-bottom: 14px;
  }}
  .stat {{
    background: var(--panel-2); border: 1px solid var(--border); border-radius: 12px;
    padding: 10px 12px;
  }}
  .stat strong {{ display: block; font-size: 1.3rem; }}
  .stat span {{ color: var(--muted); font-size: 0.78rem; }}
  .stat.ok strong {{ color: var(--pass); }}
  .stat.warn strong {{ color: var(--warn); }}
  .stat.fail strong {{ color: var(--fail); }}
  .stat.add strong {{ color: var(--add); }}
  details.block {{
    border: 1px solid var(--border); border-radius: 12px; margin-bottom: 10px;
    background: var(--panel-2); overflow: hidden;
  }}
  details.block summary {{
    cursor: pointer; padding: 12px 14px; font-weight: 650; list-style: none;
    display: flex; gap: 10px; align-items: center; flex-wrap: wrap;
  }}
  details.block summary::-webkit-details-marker {{ display: none; }}
  details.block summary::before {{ content: "▸"; color: var(--muted); }}
  details[open].block summary::before {{ content: "▾"; }}
  details.block summary em {{
    font-style: normal; background: #0f1419; border-radius: 999px;
    padding: 1px 8px; font-size: 0.8rem; color: var(--muted);
  }}
  details.fail-block {{ border-left: 3px solid var(--fail); }}
  details.add-block {{ border-left: 3px solid var(--add); }}
  details.warn-block {{ border-left: 3px solid var(--warn); }}
  details.ok-block {{ border-left: 3px solid var(--pass); }}
  details.text-block {{ border-left: 3px solid #64748b; }}
  .table-wrap {{ overflow: auto; padding: 0 8px 10px; max-height: 420px; }}
  .empty {{ color: var(--muted); padding: 8px 14px 14px; margin: 0; }}
  .text-cols {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 12px; padding: 0 14px 14px;
  }}
  .text-cols h3 {{ margin: 0 0 8px; font-size: 0.95rem; }}
  .text-cols h3.ok {{ color: var(--pass); }}
  .text-cols h3.fail {{ color: var(--fail); }}
  .text-cols h3.add {{ color: var(--add); }}
  .chips {{ display: flex; flex-wrap: wrap; gap: 6px; }}
  .chip {{
    border-radius: 999px; padding: 4px 10px; font-size: 0.78rem;
    border: 1px solid var(--border); background: #0f1419;
  }}
  .chip.ok {{ border-color: rgba(34,197,94,.35); color: #86efac; }}
  .chip.fail {{ border-color: rgba(239,68,68,.35); color: #fca5a5; }}
  .chip.add {{ border-color: rgba(56,189,248,.35); color: #7dd3fc; }}
  .footnote {{ color: var(--muted); font-size: 0.85rem; margin-top: 18px; }}
  .hidden {{ display: none !important; }}
</style>
</head>
<body>
  <div class="wrap">
    <header class="hero">
      <div>
        <h1>{esc(component)} {title_suffix} Report</h1>
        <p>{subtitle}</p>
      </div>
      <div class="kpis">
        <div class="kpi"><strong>{total}</strong><span>Locales</span></div>
        <div class="kpi"><strong>{avg_overall:.1f}%</strong><span>Avg Overall</span></div>
        <div class="kpi"><strong>{avg_struct:.1f}%</strong><span>Avg Structural Links</span></div>
        <div class="kpi"><strong style="color:var(--pass)">{pass_n}</strong><span>Pass</span></div>
        <div class="kpi"><strong style="color:var(--warn)">{warn_n}</strong><span>Warn</span></div>
        <div class="kpi"><strong style="color:var(--fail)">{fail_n}</strong><span>Fail</span></div>
        <div class="kpi"><strong style="color:var(--error)">{error_n}</strong><span>Error</span></div>
      </div>
    </header>

    <div class="filters">
      <input id="search" type="search" placeholder="Filter by locale, path, or text..." />
      <select id="statusFilter">
        <option value="all">All statuses</option>
        <option value="pass">PASS</option>
        <option value="warn">WARN</option>
        <option value="fail">FAIL</option>
        <option value="error">ERROR</option>
      </select>
      <div class="legend">
        <span><i style="background:var(--pass)"></i>Matched</span>
        <span><i style="background:var(--warn)"></i>Renamed</span>
        <span><i style="background:var(--fail)"></i>Missing</span>
        <span><i style="background:var(--add)"></i>Additional</span>
      </div>
    </div>

    <section class="panel">
      <table id="summaryTable">
        <thead>
          <tr>
            <th>Locale</th>
            <th>Overall</th>
            <th>Structural Links</th>
            <th>Exact Paths</th>
            <th>Texts</th>
            <th>Matched</th>
            <th>Renamed</th>
            <th>Missing</th>
            <th>Additional</th>
            <th>Blank≠</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {"".join(summary_rows)}
        </tbody>
      </table>
    </section>

    <div id="localeSections">
      {"".join(locale_sections)}
    </div>

    <p class="footnote">
      <strong>Exact path</strong> = URL path must match including locale slug.
      <strong>Structural</strong> = locale stripped + known slug aliases
      (e.g. integrations→integration, ru-cis→ru).
      <strong>Missing/Additional</strong> are true differences after structural normalization.
      Full Excel also available at HeaderCheck_Report.xlsx.
    </p>
  </div>

<script>
(() => {{
  const search = document.getElementById('search');
  const statusFilter = document.getElementById('statusFilter');
  const summaryRows = [...document.querySelectorAll('#summaryTable tbody tr')];
  const cards = [...document.querySelectorAll('.locale-card')];

  function applyFilters() {{
    const q = (search.value || '').trim().toLowerCase();
    const status = statusFilter.value;

    summaryRows.forEach(row => {{
      const text = row.textContent.toLowerCase();
      const st = [...row.classList].find(c => ['pass','warn','fail','error'].includes(c)) || '';
      const statusOk = status === 'all' || st === status;
      const queryOk = !q || text.includes(q);
      row.classList.toggle('hidden', !(statusOk && queryOk));
    }});

    cards.forEach(card => {{
      const text = card.textContent.toLowerCase();
      const badge = card.querySelector('.badge');
      const st = badge ? [...badge.classList].find(c => ['pass','warn','fail','error'].includes(c)) : '';
      const statusOk = status === 'all' || st === status;
      const queryOk = !q || text.includes(q);
      card.classList.toggle('hidden', !(statusOk && queryOk));
    }});
  }}

  search.addEventListener('input', applyFilters);
  statusFilter.addEventListener('change', applyFilters);
}})();
</script>
</body>
</html>
"""


def main(
    input_xlsx: str | None = None,
    output_html: str | None = None,
    component: str = "Header",
    mode: str = "cross_env",
):
    xlsx_path = input_xlsx or INPUT_XLSX
    html_path = output_html or OUTPUT_HTML
    component = component or "Header"
    mode = mode or "cross_env"

    wb = load_workbook(xlsx_path, data_only=True)
    blank_sheet = "target=_blank Mismatches"
    data = {
        "summary": rows_as_dicts(wb["Summary"]),
        "matching_links": rows_as_dicts(wb["Matching Links"]),
        "renamed_links": rows_as_dicts(wb["Renamed Slug Links"]),
        "missing_links": rows_as_dicts(wb["Missing in Target"]),
        "additional_links": rows_as_dicts(wb["Additional in Target"]),
        "matching_texts": rows_as_dicts(wb["Matching Texts"]),
        "missing_texts": rows_as_dicts(wb["Missing Texts"]),
        "additional_texts": rows_as_dicts(wb["Additional Texts"]),
        "blank_mismatches": rows_as_dicts(wb[blank_sheet]) if blank_sheet in wb.sheetnames else [],
    }
    html_doc = build_html(data, component=component, mode=mode)
    out = Path(html_path)
    out.write_text(html_doc, encoding="utf-8")
    print(f"HTML report saved to: {out}")
    print(f"Locales: {len(data['summary'])}")
    print(f"Matching links: {len(data['matching_links'])}")
    print(f"Renamed links: {len(data['renamed_links'])}")
    print(f"Missing links: {len(data['missing_links'])}")
    print(f"Additional links: {len(data['additional_links'])}")
    print(f"target=_blank mismatches: {len(data['blank_mismatches'])}")


if __name__ == "__main__":
    main()
