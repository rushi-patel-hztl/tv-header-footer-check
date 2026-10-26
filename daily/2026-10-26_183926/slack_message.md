:red_circle: **Header/footer changed vs baseline** — run 2026-10-26 18:39 UTC
113 distinct changes across 16 locales (6 move Sitecore further from AEM). Baseline: 2026-10-13_183310.
Match % by locale/component: 14 regressed, 18 improved.

:arrow_up: **Status improved**
• Footer en: WARN → **PASS**
• Footer de: WARN → **PASS**
• Footer fr: FAIL → **WARN**
• Footer pt: FAIL → **WARN**
• Footer cn: FAIL → **WARN**
• Footer hu: FAIL → **WARN**
• Footer it: FAIL → **WARN**
• Footer ko: FAIL → **WARN**
• Footer nl: FAIL → **WARN**
• Footer pl: FAIL → **WARN**
• Footer th: FAIL → **WARN**
• Footer ru: FAIL → **WARN**
• Footer cs: FAIL → **WARN**
• Footer tw: FAIL → **WARN**
• Footer tr: FAIL → **WARN**

:warning: **Needs a look: Sitecore now further from AEM**
• **Footer** · Sitecore page: Link removed "Blog" and translations → `/resources/news-insights` — 4 locales: pt, cn, ko, nl
• **Footer** · Sitecore page: Link added "Blog e notícias" and translations → `/resources/blog` — 3 locales: pt, ko, nl
• **Footer** · Sitecore page: Link added "Events & Webinars" and translations → `/resources/events` — 2 locales: cn, it
• **Footer** · Sitecore page: Link added "TeamViewer ONE" → `/platform/teamviewer-one` — 1 locale: cs

:grey_question: **Mixed effect**
• **Header** · Sitecore page: Phone number link added (`+1 239 999 4122`, `+1 727 287 3479`) — 16 locales (all except ja)
      _Phone numbers vary by visitor location; confirm before raising._
• **Header** · Sitecore page: Link removed "Company" → `/global/company` — 2 locales: en, de

_…2 more section(s) in the report._

Status vs AEM now: Header: 1 FAIL · 16 WARN  |  Footer: 14 WARN · 3 PASS
Details: [DifferenceReport.html](https://github.com/rushi-patel-hztl/tv-header-footer-check/blob/main/daily/2026-10-26_183926/DifferenceReport.html) · [Run folder](https://github.com/rushi-patel-hztl/tv-header-footer-check/tree/main/daily/2026-10-26_183926) · [run.log](https://github.com/rushi-patel-hztl/tv-header-footer-check/blob/main/daily/2026-10-26_183926/run.log)
