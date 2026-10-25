:red_circle: **Header/footer changed vs baseline** — run 2026-10-25 18:39 UTC
127 distinct changes across 16 locales (12 move Sitecore further from AEM). Baseline: 2026-10-13_183310.
Match % by locale/component: 17 regressed, 15 improved.

:arrow_up: **Status improved**
• Footer fr: FAIL → **WARN**
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
• **Footer** · Sitecore page: Link added "Webinars" → `/resources/webinars` — 11 locales: pt, cn, hu, it, ko, pl, th, ru, cs, tw, tr
• **Footer** · Sitecore page: Link added "Personal use" → `/solutions/free-for-personal-use` — 8 locales: de, fr, es, pt, cn, it, ko, nl
• **Footer** · Sitecore page: Link added "TeamViewer ONE" → `/platform/teamviewer-one` — 7 locales: hu, pl, th, ru, cs, tw, tr
• **Footer** · Sitecore page: Link added "Eventos e webinars" and translations → `/resources/events` — 6 locales: pt, cn, it, ko, nl, tw
• **Footer** · Sitecore page: Link removed "Blog" and translations → `/resources/news-insights` — 4 locales: pt, cn, ko, nl
• **Footer** · Sitecore page: Link removed "TeamViewer ONE" → `/platform/one` — 4 locales: pl, th, ru, cs
• **Header** · Sitecore page: Link removed "Dowiedz się więcej" and translations → `/platform/one` — 4 locales: pl, th, ru, cs
• **Footer** · Sitecore page: Link added "远程控制" → `/solutions/remote-control` — 1 locale: cn
• **Footer** · Sitecore page: Link added "远程桌面" → `/solutions/remote-desktop` — 1 locale: cn
• **Footer** · Sitecore page: Link added "屏幕共享" → `/solutions/screen-sharing` — 1 locale: cn

:grey_question: **Mixed effect**
• **Header** · Sitecore page: Phone number link added (`+1 239 999 4122`, `+1 727 287 3479`) — 16 locales (all except ja)
      _Phone numbers vary by visitor location; confirm before raising._
• **Header** · Sitecore page: Link removed "Company" → `/global/company` — 2 locales: en, de

_…2 more section(s) in the report._

Status vs AEM now: Header: 1 FAIL · 16 WARN  |  Footer: 2 FAIL · 14 WARN · 1 PASS
Details: [DifferenceReport.html](https://github.com/rushi-patel-hztl/tv-header-footer-check/blob/main/daily/2026-10-25_183930/DifferenceReport.html) · [Run folder](https://github.com/rushi-patel-hztl/tv-header-footer-check/tree/main/daily/2026-10-25_183930) · [run.log](https://github.com/rushi-patel-hztl/tv-header-footer-check/blob/main/daily/2026-10-25_183930/run.log)
