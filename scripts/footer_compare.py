"""
Compare footer text and links between source and target TeamViewer pages.

Reuses matching rules from header_compare.py, with footer-specific false-positive fixes:
- exclude region selector (different UX; locale strip caused fake renames)
- footer slug aliases (press→newsroom, research-projects→research--projects, …)
- light text normalization (Cookie(s) Settings, EULA / DPA, Trust Center(s))
- visible text only; skip .utils-visually-hidden; ru-cis ≡ ru; target=_blank

Reads pairs from HeaderCheck.xlsx and writes FooterCheck_Report_v5.*
(Source = locale homepage; target = KB page on www.teamviewer.com.)
"""

from __future__ import annotations

import re
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from playwright.sync_api import sync_playwright

import generate_html_report as html_report
import header_compare as hc
from header_compare import (
    compare_headers,
    load_pairs,
    locale_from_url,
    normalize_href as _normalize_href_base,
    text_key as _text_key_base,
    write_report,
)

INPUT_XLSX = r"c:\Users\rpatel\Desktop\Teamviewer\HeaderCheck.xlsx"
OUTPUT_XLSX = r"c:\Users\rpatel\Desktop\Teamviewer\FooterCheck_Report_v5.xlsx"
OUTPUT_HTML = r"c:\Users\rpatel\Desktop\Teamviewer\FooterCheck_Report_v5.html"

DROP_QUERY_KEYS = {"language-switched", "language_switched"}

# Extra path aliases seen in footer (applied via PATH_SLUG_ALIASES during compare)
FOOTER_PATH_SLUG_ALIASES = [
    (r"/global/company/press\b", "/global/company/newsroom"),
    (r"/global/company/research-projects\b", "/global/company/research--projects"),
    (r"/global/company/research_projects\b", "/global/company/research--projects"),
]


def normalize_href(href: str, *, structural: bool = False, keep_host: bool = False) -> str:
    """Header normalize + drop language-switch query noise."""
    if not href:
        return ""
    parsed = urlparse(href.strip())
    if parsed.query:
        kept = [
            (k, v)
            for k, v in parse_qsl(parsed.query, keep_blank_values=True)
            if k.lower() not in DROP_QUERY_KEYS
        ]
        href = urlunparse(
            (
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                urlencode(kept),
                "",
            )
        )
    return _normalize_href_base(href, structural=structural, keep_host=keep_host)


def text_key(text: str) -> str:
    """Footer text key with punctuation / plural noise removed."""
    t = _text_key_base(text)
    # "EULA / DPA" vs "EULA/DPA"
    t = re.sub(r"\s*/\s*", "/", t)
    t = re.sub(r"\s+", " ", t).strip()
    # Known label equivalents
    equivalents = {
        "cookies settings": "cookie settings",
        "cookie settings": "cookie settings",
        "trust centers": "trust center",
        "trust center": "trust center",
        "eula / dpa": "eula/dpa",
        "eula/dpa": "eula/dpa",
    }
    return equivalents.get(t, t)


EXTRACT_FOOTER_JS = """
() => {
  const dismissSelectors = [
    '#onetrust-accept-btn-handler',
    'button#onetrust-accept-btn-handler',
    '[aria-label="Accept All"]',
    'button[aria-label*="Accept"]',
    '.ot-sdk-container button[title*="Accept"]'
  ];
  for (const sel of dismissSelectors) {
    const btn = document.querySelector(sel);
    if (btn) { try { btn.click(); } catch (e) {} }
  }

  // Prefer the real site footer — avoid integrations bar <footer> on Sitecore
  const pickFooter = () => {
    const byId = document.querySelector('#footer');
    if (byId) return byId;

    const aem = document.querySelector(
      'footer.utils-page-footer, footer.xf-footer-general, .cmp-experiencefragment--footer'
    );
    if (aem) return aem.tagName === 'FOOTER' ? aem : (aem.querySelector('footer') || aem);

    const sitecore = document.querySelector(
      '[data-component="authorable/shared/site-structure/footer/footer"]'
    );
    if (sitecore) return sitecore;

    const footers = [...document.querySelectorAll('footer, [role="contentinfo"]')];
    if (!footers.length) return null;
    footers.sort(
      (a, b) => b.querySelectorAll('a[href]').length - a.querySelectorAll('a[href]').length
    );
    return footers[0];
  };

  const footer = pickFooter();
  if (!footer) {
    return { error: 'Footer element not found', links: [], texts: [], rawText: '' };
  }

  // Region selector differs heavily (full country list vs compact Sitecore UI)
  // and locale-stripped matching creates false renames — exclude it.
  const regionRoots = [];
  footer.querySelectorAll([
    '.regionselector',
    '.xf-footer-general__regionselector',
    '.cmp-region',
    '.cmp-regionselector',
    '[class*=\"regionselector\" i]',
    '[class*=\"region-selector\" i]',
    '[data-component*=\"region\" i]',
    '[data-name*=\"region\" i]'
  ].join(',')).forEach((el) => regionRoots.push(el));

  // Sitecore: column that contains the "Region Selector" / "Change Region" control
  const regionLabel = [...footer.querySelectorAll('span, button, p, h2, h3')].find((el) => {
    const t = (el.innerText || el.textContent || '').trim().replace(/\\s+/g, ' ');
    return /^(Region Selector|Change Region)$/i.test(t);
  });
  if (regionLabel) {
    const col =
      regionLabel.closest('[class*=\"col-span-1\"]') ||
      regionLabel.closest('.xf-footer-general__regionselector') ||
      regionLabel.closest('.regionselector') ||
      regionLabel.closest('div');
    if (col && col !== footer) regionRoots.push(col);
  }

  const isInRegionSelector = (el) => {
    if (!el) return false;
    return regionRoots.some((root) => root === el || root.contains(el));
  };

  const directText = (el) => {
    if (!el) return '';
    return [...el.childNodes]
      .filter((n) => n.nodeType === 3)
      .map((n) => (n.textContent || '').trim())
      .filter(Boolean)
      .join(' ')
      .replace(/\\s+/g, ' ')
      .trim();
  };

  const normalizeLabel = (t) => (t || '').replace(/\\s+/g, ' ').trim();

  const isVisuallyHidden = (el) => {
    if (!el || !el.closest) return false;
    return !!el.closest('.utils-visually-hidden, .sr-only, .visually-hidden');
  };

  const pickLinkLabel = (a) => {
    const titleSel = [
      '.cmp-menuitem__page-title',
      '.cmp-menuitem__title',
      'h2', 'h3', 'h4',
      'p.font-weight-bold',
      'p.font-bold',
      '.naviagation-title'
    ].join(',');
    const titleEl = a.querySelector(titleSel);
    if (titleEl && !isVisuallyHidden(titleEl)) {
      const t = normalizeLabel(directText(titleEl) || titleEl.innerText || '');
      if (t) return t.slice(0, 120);
    }
    for (const child of a.querySelectorAll('p, span, strong, b')) {
      if (isVisuallyHidden(child)) continue;
      const t = normalizeLabel(directText(child));
      if (t && t.length >= 2 && t.length <= 80) return t;
    }
    const clone = a.cloneNode(true);
    clone.querySelectorAll('.utils-visually-hidden, .sr-only, .visually-hidden').forEach((n) => n.remove());
    return normalizeLabel(clone.innerText || clone.textContent || '').slice(0, 120);
  };

  const links = [];
  const seen = new Set();
  let skippedRegionLinks = 0;
  for (const a of footer.querySelectorAll('a[href]')) {
    if (isInRegionSelector(a)) {
      skippedRegionLinks += 1;
      continue;
    }
    const href = a.href || a.getAttribute('href') || '';
    if (!href || href.startsWith('javascript:')) continue;
    const text = pickLinkLabel(a);
    const targetAttr = (a.getAttribute('target') || '').trim();
    const key = href + '||' + text + '||' + targetAttr.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    links.push({ text, href, target: targetAttr });
  }

  const texts = [];
  const textSeen = new Set();
  const addText = (raw) => {
    const t = normalizeLabel(raw);
    if (!t || t.length < 2 || t.length > 80) return;
    if (/^[+\\d\\s()-]{6,}$/.test(t)) return;
    const key = t.toLowerCase();
    if (textSeen.has(key)) return;
    textSeen.add(key);
    texts.push(t);
  };

  const collectLeaf = (el) => {
    if (!el || isVisuallyHidden(el) || isInRegionSelector(el)) return;
    const own = directText(el);
    if (own) addText(own);
  };

  footer.querySelectorAll(
    'h2, h3, h4, p, span, button, b, strong, li > a, ' +
    '.naviagation-title, .xf-footer-general__sitemap a, ' +
    '[data-component*=\"footer\"] a'
  ).forEach(collectLeaf);

  footer.querySelectorAll('a').forEach(collectLeaf);

  // Sitemap / legal block only for rawText sample (region stripped via clone)
  const clone = footer.cloneNode(true);
  // Remove known region roots from clone by matching similar selectors / label column
  clone.querySelectorAll([
    '.regionselector',
    '.xf-footer-general__regionselector',
    '.cmp-region',
    '.cmp-regionselector',
    '[class*=\"regionselector\" i]',
    '[data-component*=\"region\" i]',
    '[data-name*=\"region\" i]'
  ].join(',')).forEach((n) => n.remove());
  const cloneLabel = [...clone.querySelectorAll('span, button, p, h2, h3')].find((el) => {
    const t = (el.innerText || el.textContent || '').trim().replace(/\\s+/g, ' ');
    return /^(Region Selector|Change Region)$/i.test(t);
  });
  if (cloneLabel) {
    const col =
      cloneLabel.closest('[class*=\"col-span-1\"]') ||
      cloneLabel.closest('div');
    if (col) col.remove();
  }

  return {
    error: null,
    links,
    texts,
    rawText: (clone.innerText || '').trim().replace(/\\s+/g, ' ').slice(0, 5000),
    linkCount: links.length,
    textCount: texts.length,
    skippedRegionLinks,
    footerTag: footer.tagName,
    footerId: footer.id || '',
    footerClass: (footer.className || '').toString().slice(0, 160)
  };
}
"""


def extract_footer(page, url: str) -> dict:
    last_err = None
    for attempt in range(1, 4):
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=90000)
            last_err = None
            break
        except Exception as e:
            last_err = e
            page.wait_for_timeout(1500 * attempt)
    if last_err:
        raise last_err

    page.wait_for_timeout(2000)
    for sel in [
        "#onetrust-accept-btn-handler",
        'button:has-text("Accept All")',
        'button:has-text("Accept all")',
        'button:has-text("Alle akzeptieren")',
        'button:has-text("Tout accepter")',
    ]:
        try:
            loc = page.locator(sel).first
            if loc.is_visible(timeout=1500):
                loc.click(timeout=2000)
                page.wait_for_timeout(500)
                break
        except Exception:
            continue

    try:
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(2500)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(1500)
    except Exception:
        pass

    try:
        page.locator(
            "#footer, footer.utils-page-footer, footer.xf-footer-general, "
            '[data-component="authorable/shared/site-structure/footer/footer"]'
        ).first.wait_for(state="attached", timeout=15000)
    except Exception:
        pass

    data = page.evaluate(EXTRACT_FOOTER_JS)
    data["final_url"] = page.url
    data["requested_url"] = url
    return data


def main():
    # Footer-aware matching hooks for this run only
    original_normalize = hc.normalize_href
    original_text_key = hc.text_key
    original_aliases = list(hc.PATH_SLUG_ALIASES)

    hc.normalize_href = normalize_href
    hc.text_key = text_key
    hc.PATH_SLUG_ALIASES = original_aliases + FOOTER_PATH_SLUG_ALIASES

    try:
        pairs = load_pairs(INPUT_XLSX)
        print(f"Loaded {len(pairs)} unique pairs (FOOTER check v2 — false positives reduced)")
        results = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                viewport={"width": 1440, "height": 900},
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0.0.0 Safari/537.36"
                ),
                ignore_https_errors=True,
            )
            page = context.new_page()
            page.set_default_timeout(60000)

            for idx, (source_url, target_url) in enumerate(pairs, 1):
                locale = locale_from_url(source_url)
                print(f"\n[{idx}/{len(pairs)}] Locale={locale}")
                print(f"  Source: {source_url}")
                src_data = {"error": None, "links": [], "texts": []}
                tgt_data = {"error": None, "links": [], "texts": []}
                try:
                    src_data = extract_footer(page, source_url)
                    print(
                        f"  Source links={src_data.get('linkCount')} "
                        f"texts={src_data.get('textCount')} "
                        f"skippedRegion={src_data.get('skippedRegionLinks')} "
                        f"el={src_data.get('footerTag')}#{src_data.get('footerId')}"
                    )
                except Exception as e:
                    src_data["error"] = str(e)
                    print(f"  Source ERROR: {e}")

                print(f"  Target: {target_url}")
                try:
                    tgt_data = extract_footer(page, target_url)
                    print(
                        f"  Target links={tgt_data.get('linkCount')} "
                        f"texts={tgt_data.get('textCount')} "
                        f"skippedRegion={tgt_data.get('skippedRegionLinks')} "
                        f"el={tgt_data.get('footerTag')}#{tgt_data.get('footerId')}"
                    )
                except Exception as e:
                    tgt_data["error"] = str(e)
                    print(f"  Target ERROR: {e}")

                comparison = compare_headers(src_data, tgt_data)
                print(
                    f"  Overall={comparison['overall_match_pct']}% "
                    f"StructLinks={comparison['link_match_pct']}% "
                    f"ExactLinks={comparison['exact_link_match_pct']}% "
                    f"Texts={comparison['text_match_pct']}% "
                    f"Renamed={comparison['renamed_link_count']} "
                    f"Missing={comparison['missing_link_count']} "
                    f"Additional={comparison['additional_link_count']} "
                    f"BlankMismatch={comparison['target_blank_mismatch_count']}"
                )
                results.append(
                    {
                        "locale": locale,
                        "source_url": source_url,
                        "target_url": target_url,
                        "source": src_data,
                        "target": tgt_data,
                        "comparison": comparison,
                    }
                )

            browser.close()

        write_report(results, OUTPUT_XLSX)
        print(f"\nReport saved to: {OUTPUT_XLSX}")

        try:
            html_report.main(
                input_xlsx=OUTPUT_XLSX,
                output_html=OUTPUT_HTML,
                component="Footer",
            )
            print(f"HTML report saved to: {OUTPUT_HTML}")
        except Exception as html_err:
            print(f"HTML report generation skipped: {html_err}")

        print("\n" + "=" * 120)
        print(
            f"{'Locale':<8} {'Overall%':>9} {'Struct%':>9} {'Exact%':>9} {'Text%':>8} "
            f"{'Rename':>7} {'Miss':>5} {'Add':>5} {'BlankMM':>7} {'Status':>8}"
        )
        print("=" * 120)
        for r in results:
            c = r["comparison"]
            overall = c["overall_match_pct"]
            status = (
                "ERROR"
                if r["source"].get("error") or r["target"].get("error")
                else "PASS"
                if overall >= 95 and c["missing_link_count"] == 0
                else "WARN"
                if overall >= 80
                else "FAIL"
            )
            print(
                f"{r['locale']:<8} {overall:>9.2f} {c['link_match_pct']:>9.2f} "
                f"{c['exact_link_match_pct']:>9.2f} {c['text_match_pct']:>8.2f} "
                f"{c['renamed_link_count']:>7} {c['missing_link_count']:>5} "
                f"{c['additional_link_count']:>5} {c['target_blank_mismatch_count']:>7} "
                f"{status:>8}"
            )
        print("=" * 120)
    finally:
        hc.normalize_href = original_normalize
        hc.text_key = original_text_key
        hc.PATH_SLUG_ALIASES = original_aliases


if __name__ == "__main__":
    main()
