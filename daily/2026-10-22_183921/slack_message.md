:red_circle: **Header/footer changed vs baseline** — run 2026-10-22 18:39 UTC
135 distinct changes across 16 locales (21 move Sitecore further from AEM). Baseline: 2026-10-13_183310.
Match % by locale/component: 20 regressed, 12 improved.

:arrow_up: **Status improved**
• Footer fr: FAIL → **WARN**
• Footer hu: FAIL → **WARN**
• Footer it: FAIL → **WARN**
• Footer ko: FAIL → **WARN**
• Footer nl: FAIL → **WARN**
• Footer pl: FAIL → **WARN**
• Footer ru: FAIL → **WARN**
• Footer cs: FAIL → **WARN**
• Footer tw: FAIL → **WARN**
• Footer tr: FAIL → **WARN**

:warning: **Needs a look: Sitecore now further from AEM**
• **Footer** · Sitecore page: Link removed "Blog" and translations → `/resources/news-insights` — 14 locales (all except es, ja, it)
• **Header** · Sitecore page: Link removed "Blog" and translations → `/resources/news-insights` — 14 locales (all except es, ja, it)
• **Footer** · Sitecore page: Link removed "Customer stories" and translations → `/resources/success-stories` — 13 locales (all except es, ja, hu, it)
• **Footer** · Sitecore page: Link removed "Trust Center" and translations → `/resources/trust-center` — 13 locales (all except es, ja, hu, it)
• **Header** · Sitecore page: Link removed "Success stories" and translations → `/resources/success-stories` — 13 locales (all except es, ja, hu, it)
• **Footer** · Sitecore page: Link added "Personal use" → `/solutions/free-for-personal-use` — 8 locales: de, fr, es, pt, cn, it, ko, nl
• **Footer** · Sitecore page: Link added "TeamViewer ONE" → `/platform/teamviewer-one` — 7 locales: hu, pl, th, ru, cs, tw, tr
• **Footer** · Sitecore page: Link removed "TeamViewer ONE" → `/platform/one` — 5 locales: cn, pl, th, ru, cs
• **Header** · Sitecore page: Link removed "了解详情" and translations → `/platform/one` — 5 locales: cn, pl, th, ru, cs
• **Footer** · Sitecore page: Link added "Webinars" → `/resources/webinars` — 3 locales: es, hu, it
• **Footer** · Sitecore page: Link label changed to "News and insights" (was "Blog") on `/resources/news-insights` — 2 locales: es, it
• **Footer** · Sitecore page: Link added "Blog" → `/resources/blog` — 1 locale: es
• **Footer** · Sitecore page: Link added "Glosario" → `/resources/glossary` — 1 locale: es
• **Footer** · Sitecore page: Link added "远程控制" → `/solutions/remote-control` — 1 locale: cn
• **Footer** · Sitecore page: Link added "远程桌面" → `/solutions/remote-desktop` — 1 locale: cn
• **Footer** · Sitecore page: Link added "屏幕共享" → `/solutions/screen-sharing` — 1 locale: cn
• **Footer** · Sitecore page: Link added "Eventi e webinar" → `/resources/events` — 1 locale: it

:grey_question: **Mixed effect**
• **Header** · Sitecore page: Phone number link added (`+1 239 999 4122`, `+1 727 287 3479`) — 16 locales (all except ja)
      _Phone numbers vary by visitor location; confirm before raising._
• **Footer** · Sitecore page: Link removed "Events and webinars" and translations → `/resources/events` — 4 locales: en, de, fr, cs
• **Footer** · Sitecore page: Link removed "Why TeamViewer" → `/resources/compare` — 2 locales: en, es
• **Header** · Sitecore page: Link removed "Company" → `/global/company` — 2 locales: en, de

_…2 more section(s) in the report._

Status vs AEM now: Header: 1 FAIL · 16 WARN  |  Footer: 3 FAIL · 13 WARN · 1 PASS
Details: [DifferenceReport.html](https://github.com/rushi-patel-hztl/tv-header-footer-check/blob/main/daily/2026-10-22_183921/DifferenceReport.html) · [Run folder](https://github.com/rushi-patel-hztl/tv-header-footer-check/tree/main/daily/2026-10-22_183921) · [run.log](https://github.com/rushi-patel-hztl/tv-header-footer-check/blob/main/daily/2026-10-22_183921/run.log)
