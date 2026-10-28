:red_circle: **Header/footer changed vs baseline** — run 2026-10-28 18:40 UTC
543 distinct changes across 17 locales (19 move Sitecore further from AEM). Baseline: 2026-10-13_183310.
Match % by locale/component: 32 improved, 2 regressed.

:rotating_light: **Status got worse**
• Footer ja: PASS → **WARN**

:arrow_up: **Status improved**
• Header en: FAIL → **WARN**
• Footer en: WARN → **PASS**
• Footer de: WARN → **PASS**
• Footer fr: FAIL → **PASS**
• Footer es: WARN → **PASS**
• Footer pt: FAIL → **PASS**
• Footer cn: FAIL → **PASS**
• Footer hu: FAIL → **PASS**
• Footer it: FAIL → **PASS**
• Footer ko: FAIL → **PASS**
• Footer nl: FAIL → **PASS**
• Footer pl: FAIL → **PASS**
• Footer th: FAIL → **PASS**
• Footer ru: FAIL → **PASS**
• Footer cs: FAIL → **PASS**
• Footer tw: FAIL → **PASS**
• Footer tr: FAIL → **PASS**

:warning: **Needs a look: Sitecore now further from AEM**
• **Footer** · AEM home page: Link removed "None" → `note.com/teamviewerjapan` (Sitecore page still has it) — 1 locale: ja
• **Footer** · AEM home page: Link removed "None" → `x.com/teamviewerjp` (Sitecore page still has it) — 1 locale: ja
• **Footer** · AEM home page: Link label changed to "None" (was "Cookie 設定") on `/ja` — 1 locale: ja
• **Footer** · AEM home page: Link URL changed "None" → `/ja` — 1 locale: ja
• **Footer** · AEM home page: Text "TeamViewerジャパンのサイトに戻る" added — 1 locale: ja
• **Footer** · AEM home page: Text "地域を変更" added — 1 locale: ja
• **Footer** · AEM home page: Text "日本のお客様向けの情報は、日本のWebサイトにてご提供しております。" added — 1 locale: ja

:grey_question: **Mixed effect**
• **Header** · AEM home page: Phone number link added (`+1 239 999 4122`, `+1 727 287 3479`) — all 17 locales
      _Phone numbers vary by visitor location; confirm before raising._
• **Footer** · AEM home page: Link added "About Teamviewer" and translations → `/global/company` — all 17 locales
• **Header** · AEM home page: Link removed "Management Console" and translations → `login.teamviewer.com/logon` — all 17 locales
• **Header** · AEM home page: Link removed "Customer Portal" and translations → `service.teamviewer.com` — all 17 locales
• **Header** · AEM home page: Link removed "Ticket" and translations → `support.teamviewer.com` — all 17 locales
• **Header** · AEM home page: Link removed "Open web app" and translations → `web.teamviewer.com` — all 17 locales
• **Footer** · AEM home page: Link removed "None" → `/` — 16 locales (all except cn)
• **Footer** · AEM home page: Link added "TeamViewer United States" → `/en-us` — 16 locales (all except en)
• **Header** · AEM home page: Phone number link removed (`+49 7161 60692 50`, `+33 1 70 70 12 22`, `+34 91 7697 870`) — 15 locales (all except en, ru)
      _Phone numbers vary by visitor location; confirm before raising._
• **Footer** · AEM home page: Link added "Contacter le service commercial" and translations → `/global/company/contact-sales` — 14 locales (all except en, de, es)
• **Footer** · AEM home page: Link removed "Contacter le service commercial" and translations → `/global/contact-sales` — 14 locales (all except en, de, es)
• **Header** · Sitecore page: Link removed "Company" → `/global/company` — 2 locales: en, de

_…2 more section(s) in the report._

Status vs AEM now: Header: 17 WARN  |  Footer: 1 WARN · 16 PASS
Details: [DifferenceReport.html](https://github.com/rushi-patel-hztl/tv-header-footer-check/blob/main/daily/2026-10-28_184003/DifferenceReport.html) · [Run folder](https://github.com/rushi-patel-hztl/tv-header-footer-check/tree/main/daily/2026-10-28_184003) · [run.log](https://github.com/rushi-patel-hztl/tv-header-footer-check/blob/main/daily/2026-10-28_184003/run.log)
