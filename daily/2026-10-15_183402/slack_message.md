:red_circle: **Header/footer changed vs baseline** — run 2026-10-15 18:34 UTC
14 distinct changes across 16 locales (2 move Sitecore further from AEM). Baseline: 2026-10-13_183310.
Match % by locale/component: 16 improved, 16 regressed.

:arrow_up: **Status improved**
• Footer fr: FAIL → **WARN**
• Footer pt: FAIL → **WARN**
• Footer cn: FAIL → **WARN**
• Footer hu: FAIL → **WARN**
• Footer it: FAIL → **WARN**
• Footer ko: FAIL → **WARN**
• Footer nl: FAIL → **WARN**
• Footer th: FAIL → **WARN**
• Footer ru: FAIL → **WARN**

:warning: **Needs a look: Sitecore now further from AEM**
• **Footer** · AEM home page: Link removed "Make work work better" → `/special/make-work-work-better` (Sitecore page still has it) — 2 locales: en, de

:grey_question: **Mixed effect**
• **Header** · Sitecore page: Phone number link added (`+1 239 999 4122`, `+1 727 287 3479`) — 16 locales (all except ja)
      _Phone numbers vary by visitor location; confirm before raising._

:information_source: **Other changes (check they are intended)**
• **Footer** · Sitecore page: Text "Solutions" added — 3 locales: hu, ru, tw
• **Footer** · Sitecore page: Link label changed to "Use cases" (was localised, e.g. "По сценариям использования") on `/solutions/use-cases` — 3 locales: ru, tw, tr
• **Footer** · Sitecore page: Text "Megoldások" removed — 1 locale: hu
• **Footer** · Sitecore page: Link label changed to "Według zastosowań" (was "Według zastosowań (use cases)") on `/solutions/use-cases` — 1 locale: pl
• **Footer** · Sitecore page: Text "Решения" removed — 1 locale: ru
• **Footer** · Sitecore page: Text "解決方案" removed — 1 locale: tw
• **Header** · Sitecore page: Link label changed to "Voor grote ondernemingen" (was "Enterprise") on `/enterprise` — 1 locale: nl
• **Header** · Sitecore page: Link label changed to "Цифровой опыт сотрудников" (was "Digital Employee Experience") on `/platform/one/features/digital-employee-experience` — 1 locale: ru
• **Header** · Sitecore page: Link label changed to "Kurumsal" (was "Enterprise") on `/enterprise` — 1 locale: tr

:white_check_mark: **Sitecore now closer to AEM (confirm intended)**
• **Footer** · Sitecore page: Link removed "Existing Partner Login" and translations → `/partner/existing-partner-login` — 16 locales (all except ja)
• **Footer** · Sitecore page: Link removed "Les dirigeants (EN)" and translations → `/global/company/leadership` — 12 locales (all except en, de, ja, pt, pl)
• **Footer** · Sitecore page: Link removed "Sponsoring sportif (EN)" and translations → `/global/company/sponsorship` — 11 locales: fr, es, pt, hu, it, ko, nl, pl, th, ru, cs

Status vs AEM now: Header: 1 FAIL · 16 WARN  |  Footer: 4 FAIL · 12 WARN · 1 PASS
Details: [DifferenceReport.html](https://github.com/rushi-patel-hztl/tv-header-footer-check/blob/main/daily/2026-10-15_183402/DifferenceReport.html) · [Run folder](https://github.com/rushi-patel-hztl/tv-header-footer-check/tree/main/daily/2026-10-15_183402) · [run.log](https://github.com/rushi-patel-hztl/tv-header-footer-check/blob/main/daily/2026-10-15_183402/run.log)
