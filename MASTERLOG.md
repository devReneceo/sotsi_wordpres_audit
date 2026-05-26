# SOTSI WordPress Audit — Masterlog

> Este es el **MASTERLOG** del proyecto SOTSI (renombrado de `WORK_LOG.md` el 2026-05-25).
> Registro maestro de toda la auditoría + migración a Webflow.

**Site:** seatofthesoul.com
**Repo:** devReneceo/sotsi_wordpres_audit
**Live URL:** https://devreneceo.github.io/sotsi_wordpres_audit/

---

## How to regenerate everything (quick reference)

Three scripts, run in this order. Zero pip dependencies — stdlib Python 3 only. No API key required.

```bash
cd "/Users/joeldoradoaguilus/Documents/22D Marketing/SOTSI-WordPress-Audit"

# 1. Pull fresh blog post content from WordPress + classify each post.
#    Outputs: data/posts_extracted.json + BLOG_MIGRATION_TRIAGE.md
python3 extract_blog_data.py

# 2. Rebuild the web audit report (includes the Blog Migration Triage tab).
#    Outputs: SOTSI_Audit_Report.html
python3 audit_sotsi.py

# 3. Build the executive PDF for Christopher.
#    Outputs: SOTSI_Blog_Migration_Triage_Report.html (print-ready)
#             SOTSI_Blog_Migration_Triage_Report.pdf  (final deliverable)
python3 generate_triage_pdf.py
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="SOTSI_Blog_Migration_Triage_Report.pdf" \
  "file://$(pwd)/SOTSI_Blog_Migration_Triage_Report.html"

# 4. Build Christopher's CSV spreadsheets (Excel/Sheets/Numbers ready).
#    Outputs: SOTSI_Blog_Posts_Triage.csv   (all 187 posts, full detail)
#             SOTSI_Blog_Posts_Drops.csv    (slim view, 20 drops only)
#             SOTSI_Blog_SEO_QuickWins.csv  (167 keeps, worst-first by SEO score)
python3 generate_spreadsheet.py

# 5. Push the web report to GitHub Pages.
cp SOTSI_Audit_Report.html index.html
git add -A
git commit -m "update: refresh audit"
git push
```

GitHub Pages updates in ~1 minute after push.

### What each script does

| Script | Purpose | Inputs | Outputs |
|---|---|---|---|
| `extract_blog_data.py` | Pulls full blog post bodies from WP API, runs deterministic triage rules, emits machote MD | live WP REST API on seatofthesoul.com | `data/posts_extracted.json` (~480 KB), `BLOG_MIGRATION_TRIAGE.md` (~220 KB) |
| `audit_sotsi.py` | Builds the interactive web reporter with all tabs (Pages, Posts, Triage, Sitemap, etc.) | live WP API + `data/posts_extracted.json` | `SOTSI_Audit_Report.html` (~470 KB, self-contained) |
| `generate_triage_pdf.py` | Builds the executive print-ready HTML for Christopher | `data/posts_extracted.json` | `SOTSI_Blog_Migration_Triage_Report.html` (print-only) |
| `generate_spreadsheet.py` | Builds Christopher's CSVs (full triage + drops only + SEO quick wins) with deterministic SEO scoring | `data/posts_extracted.json` | `SOTSI_Blog_Posts_Triage.csv`, `SOTSI_Blog_Posts_Drops.csv`, `SOTSI_Blog_SEO_QuickWins.csv` |

### Common single-task flows

**Just refresh the web report after WordPress changes:**
```bash
python3 extract_blog_data.py && python3 audit_sotsi.py && cp SOTSI_Audit_Report.html index.html && git add -A && git commit -m "update: refresh" && git push
```

**Just regenerate Christopher's PDF (no web changes):**
```bash
python3 extract_blog_data.py && python3 generate_triage_pdf.py
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu --no-pdf-header-footer --print-to-pdf="SOTSI_Blog_Migration_Triage_Report.pdf" "file://$(pwd)/SOTSI_Blog_Migration_Triage_Report.html"
```

---

## Session · 2026-04-30

### Task: Full WordPress site audit for Christopher's request

Christopher asked:
- Total active/live pages (most important)
- Total inactive/draft pages if easy to find
- Breakdown: main nav pages vs blog posts

---

### What was built

#### 1. Python scraper (`audit_sotsi.py`)
- Pulls data from WP REST API (`/wp-json/wp/v2/pages`, `/wp-json/wp/v2/posts`)
- Parses sitemap XML (`wp-sitemap.xml` → 11 nested sitemaps)
- Scrapes main navigation links from HTML
- Generates a self-contained HTML report

**Results pulled:**
| Metric | Count |
|---|---|
| Active / Live Pages | 110 |
| Blog Posts (published) | 166 |
| Draft Pages (WP Admin) | 35 |
| Draft Posts (WP Admin) | 17 |
| Main Nav Links | 14 |
| Sitemap URLs | 820 |

---

#### 2. HTML Report — Tabs

| Tab | Description |
|---|---|
| **Executive Summary** | Category + year breakdown of the 110 active pages. Click any category row → modal with filtered table |
| **Main Navigation** | 14 nav links with iframe preview panel (slide-in, loading spinner) |
| **Active Pages** | All 110 published pages — Tabulator table with virtual scroll. Click row → right-side preview panel |
| **Classification** | 110 pages classified into 5 categories with filter buttons |
| **Draft Pages** | 35 draft pages + 17 draft posts from WP Admin |
| **Blog Posts** | 166 published posts — sorted newest first |
| **Sitemap Breakdown** | 11 sitemap tiles, click to expand and browse URLs inline |

---

#### 3. Page Classification (5 categories)

| Category | Description |
|---|---|
| **Main Site** | Core brand/nav pages (About, Podcast, Books, etc.) |
| **Program / Event** | Registration, waitlists, questionnaires, SPP/APSP/SPT pages |
| **Content** | Articles, tools, tributes, assessments |
| **System** | Cart, checkout, account, privacy, membership |
| **Thank You** | Confirmation/redirect pages after form submissions |

**Potential duplicates detected:** `blog` + `blog-2`, multiple SPP/SPT registration pages for same year.

---

#### 4. Draft Pages hardcoded (not accessible via public API)

- **35 draft pages** — provided from WP Admin (pages section)
- **17 draft posts** — provided from WP Admin (posts section)

---

#### 5. Key UX features

- Right-side slide panel (50% screen) on row click in Active Pages and Blog Posts
- Category drill-down modal from Executive Summary bars
- iframe loading spinner + blocked-site fallback with "Open in new tab"
- ESC key closes any open panel/modal
- Tabulator v6 with virtual scroll (no pagination needed for 110+ rows)
- Sitemap tiles expand inline with searchable URL table

---

#### 6. Deployment

- Repo: `https://github.com/devReneceo/sotsi_wordpres_audit`
- Live URL: `https://devreneceo.github.io/sotsi_wordpres_audit/`
- Hosted via GitHub Pages (repo set to public)

---

### To regenerate the report

```bash
cd "/Users/joeldoradoaguilus/Documents/22D Marketing/SOTSI-WordPress-Audit"
python3 audit_sotsi.py
cp SOTSI_Audit_Report.html index.html
git add . && git commit -m "update: refresh audit data" && git push
```

GitHub Pages updates in ~1 minute after push.

---

### Pending / Future

- [ ] Classify blog posts by category/topic
- [ ] Add year filter to Blog Posts tab
- [ ] Schedule auto-regeneration via GitHub Actions (weekly cron)
- [ ] Get exact inactive page count from WP Admin (private + trash)

---

## Session · 2026-05-13 — Blog Migration Triage (full pipeline)

### Task from Christopher

Christopher asked over WhatsApp (2026-05-13):

1. Review every old SOTSI blog post and flag entries with dated content, references to past events, old news, or expired announcements — anything that should **not** migrate to the new site.
2. Rate the remaining (non-outdated) posts on quality.
3. Suggest SEO improvements for the keepers.
4. For new blog content, plan to repurpose Wisdom Wednesdays, Soul Seeds, Soul Snacks, top-performing FB/IG posts, and team videos.

This session delivered #1 in full. #2, #3, and #4 are deferred to follow-up sessions.

### Architecture decision — Python-first, no paid API

Joel runs the Claude monthly plan ($100/mo), not the Anthropic API. Therefore:

- Python does **all** heavy lifting: WP REST fetch, HTML parsing, deterministic heuristics, classification, PDF prep.
- Zero `ANTHROPIC_API_KEY`. Zero `anthropic` SDK dependency. Zero pip dependencies — stdlib only.
- AI (Claude) is only used during a Claude Code session to inspect ambiguous cases and to QA the output.

### Sprint 1 — Extraction + machote MD

New script: **`extract_blog_data.py`** (stdlib only). What it does:

- Fetches every published blog post from `/wp-json/wp/v2/posts` with `content.rendered`, `excerpt`, `categories`, `yoast_head_json`.
- Resolves WP category IDs to names via `/wp-json/wp/v2/categories`.
- Parses each post body with stdlib `html.parser` to extract: headings (H1–H4), image count + missing alts, internal/external link counts, word count.
- Applies deterministic heuristics (no AI per post):
  1. WP category includes `Exclude` → `auto_drop` (the SOTSI team already pre-tagged these in WordPress).
  2. Slug or title matches `soul-snack-*` / `soul-feast-*` / `soul-seed-*` / `wisdom-wednesday-*` → `auto_keep` (evergreen series).
  3. Event-keyword regex (`register`, `Zoom`, `RSVP`, `tickets`, `webinar`, `early bird`, `save the date`, etc.) + past-year regex for the remaining posts.
- Outputs:
  - `data/posts_extracted.json` — structured payload (~480 KB).
  - `BLOG_MIGRATION_TRIAGE.md` — human-readable working triage (~220 KB, 4 sections).

**Results after first pass:**

| Bucket | Posts | Notes |
|---|---:|---|
| `auto_drop` | **20** | All `Exclude`-tagged in WP — confirms decisions already made by the SOTSI editorial team |
| `auto_keep` | **167** | Soul Snacks / Feasts / Seeds / Wisdom Wednesdays — the core evergreen catalog |
| Manual review | **0** | Every post resolved by deterministic rules — no per-post AI tokens spent |

Total: 187 published posts (site grew from 166 since April 30 audit).

### Sprint 2 — Web reporter integration

Extended `audit_sotsi.py` to surface the triage inside the existing dashboard at `SOTSI_Audit_Report.html`:

- New tab **Blog Migration Triage** (next to Blog Posts) with verdict badges, chip filters (All / KEEP / DROP / REVIEW), search, and slide-panel preview reusing the existing iframe UX.
- New KPI card in the report header — clickable, jumps to the triage tab.
- Reads `data/posts_extracted.json` and embeds the rows into the self-contained HTML.
- Refreshed counts site-wide: pages 110, posts 187, sitemap URLs 858, nav 14.

### Sprint 3 — Deep content audit

After Joel asked "¿solo 20 son para eliminar? ¿los demás no son eventos?", a second pass ran a deeper scan over **the full body** of every keep-list post (not just title/excerpt). Nine independent regex patterns were checked:

| Pattern | What it would catch | Posts flagged |
|---|---|---:|
| Register by / registration opens / closes | Expired registration calls | 0 |
| Tickets / RSVP / seats remaining | Past ticketed events | 0 |
| Save the date / doors open / early bird | Promotional event language | 0 |
| Webinar on / starts on (specific date) | Specific dated webinars | 0 |
| Join us on [date] / live event / live broadcast | Past live broadcasts | 0 |
| Annual / this year's retreat or conference | Year-specific recurring events | 0 |
| Specific Month + Year in body (e.g., "March 2024") | Posts anchored to a past month | 0 |
| Specific calendar date (e.g., "October 15") | Date-specific announcements | 0 |
| Past-year-only references (body says "2023") | Time-stamped commentary | 0 |

Three phrases did appear across many keep-list posts and were inspected in context. Each was confirmed evergreen:

| Phrase | Why it appears | Verdict |
|---|---|---|
| "This week, notice…" | Recurring closing exercise (Soul Step Challenge) at the end of every Soul Snack / Feast. Reader applies the teaching during their own week — not on a specific date. | Evergreen |
| "Join Gary LIVE every month" | CTA for the ongoing Soul Themes program. Permanent and recurring monthly. | Evergreen |
| "December 14th, 2012" | One post (Soul Feast #83 with Scarlett Lewis) references the Sandy Hook anniversary as biographical context. | Evergreen |

**Confidence statement:** all 167 keep-list posts were scanned at full-body depth. Zero matched any pattern indicating a past event, expired registration, or moment-in-time announcement. The 20-post drop list is complete.

### Sprint 4 — Executive PDF for Christopher

New script: **`generate_triage_pdf.py`**. Produces a print-optimized HTML (`SOTSI_Blog_Migration_Triage_Report.html`) that Chrome headless renders to PDF (`SOTSI_Blog_Migration_Triage_Report.pdf`, ~590 KB, ~13 pages).

Style chosen: sober corporate. Helvetica, black on white, navy (#1c2333) accent only in headings. No emoji, no AI branding, no icons. Thin-border tables. Print-safe.

Final structure:

| Page | Section |
|---|---|
| 1 | Cover — "SOTSI · Blog Migration Triage Report · Prepared for Christopher Dilts" |
| 2 | Executive Summary (KPIs, method, headline finding) |
| 3 | **Section 2 — Methodology** (9 patterns checked + 3 explained-away + confidence statement) |
| 4–5 | **Section 1 — Posts to drop (20)** with title, category, year, reason |
| 6 | **Section 3 — Posts to keep (167)** summary: by series, by year, top categories |
| 7–12 | **Section 3.1 — Full keep list** with title, series, year |
| 13 | Next steps |

The methodology block also got mirrored into the web reporter as a collapsible card on the Triage tab.

### Files produced this session

| File | Type | Purpose |
|---|---|---|
| `extract_blog_data.py` | new | WP fetch + triage extractor |
| `generate_triage_pdf.py` | new | Executive PDF generator |
| `audit_sotsi.py` | modified | Added Triage tab + KPI card + methodology box |
| `data/posts_extracted.json` | new | Source of truth for triage data |
| `BLOG_MIGRATION_TRIAGE.md` | new | Working triage in markdown |
| `SOTSI_Blog_Migration_Triage_Report.html` | new | Print-ready source for the PDF |
| `SOTSI_Blog_Migration_Triage_Report.pdf` | new | Final deliverable for Christopher |
| `SOTSI_Audit_Report.html` / `index.html` | regenerated | Web report with refreshed counts and triage tab |
| `.gitignore` | new | Ignores `__pycache__`, `.env`, `.claude/` |

### Headline numbers delivered

- **20 posts** recommended **DROP** — fully listed in PDF Section 1
- **167 posts** recommended **KEEP** — evergreen Soul Snacks/Feasts/Seeds/Wisdom Wednesdays
- **89%** of the blog catalog migrates as-is
- **0** posts outside the existing `Exclude` set surfaced as event-tied after deep audit

### Still pending (for the next session)

- [ ] **Quality rating** per keep-list post (5-dimension rubric).
- [ ] **Content Pipeline tab** scaffold for Wisdom Wednesdays / Soul Seeds / top FB / IG / YouTube content. Source format and ingestion pending input from Luna.
- [ ] **GitHub Action** for weekly auto-refresh (optional).
- [ ] **Year filter** + **category filter** on Blog Posts tab.
- [ ] Confirm whether the upcoming new site is WordPress (so SEO output maps directly to Yoast) or another platform.

---

## Session · 2026-05-14 — Christopher's CSV deliverable + SEO quick wins

### Task

Joel asked for an Excel/Sheets-friendly spreadsheet for Christopher covering all 187 blog posts plus the 20 drops, with URLs as a column and basic SEO recommendations per post.

### What was built

New script: **`generate_spreadsheet.py`** (stdlib only, no pip, no API key). Reads `data/posts_extracted.json` and emits three CSVs encoded as UTF-8-BOM so Excel honours accents on open:

| File | Rows | Purpose |
|---|---:|---|
| `SOTSI_Blog_Posts_Triage.csv` | 187 | Full detail: URL, verdict, title, series, category, date, word count, image stats, link stats, Yoast title/desc, SEO score, SEO action items |
| `SOTSI_Blog_Posts_Drops.csv` | 20 | Slim view of drops only — URL, title, year, category, reason, word count, date |
| `SOTSI_Blog_SEO_QuickWins.csv` | 167 | KEEPs sorted worst-first by SEO score; top 3 action items per row |

### Deterministic SEO scoring (no AI)

Five axes, 20 points each (100 max). Score and action items computed for KEEPs only — DROPs leave those columns blank because they're going away.

| Axis | Full marks | Action emitted when failing |
|---|---|---|
| Yoast title length | 30–65 chars | "Title too long (X chars, aim 30-65)" / "Add SEO title" |
| Meta description length | 120–160 chars | "Add meta description (120-160 chars)" |
| Word count | ≥ 500 words | "Thin content" (< 300) / "Short content" (300–499) |
| Alt text coverage | All images have alt | "Add alt text to N of M images" |
| Internal links | ≥ 3 | "Add internal links (currently N, aim 3+)" |

H1 check: only flags duplicates inside the body, since the WP theme renders the post title as the page H1 outside `content.rendered` — every post would otherwise be a false positive.

### Headline findings on the 167 keepers

- **Average SEO score:** 46.9 / 100 — low, but the gap is concentrated in two fixes.
- **166 of 167** have no Yoast meta description. Fixing only that lifts average to ~67.
- **167 of 167** have fewer than 3 internal links.
- ~40 posts have titles over 65 characters (Soul Feast title pattern adds episode number + colon + topic).
- Dozens of posts have 300–500 word bodies (Soul Snack format is naturally short).

### Files produced this session

| File | Type |
|---|---|
| `generate_spreadsheet.py` | new |
| `SOTSI_Blog_Posts_Triage.csv` | new |
| `SOTSI_Blog_Posts_Drops.csv` | new |
| `SOTSI_Blog_SEO_QuickWins.csv` | new |
| `WORK_LOG.md` → `MASTERLOG.md` | renamed 2026-05-25 (este archivo) |

---

## Session · 2026-05-25 — Plan de migración a Webflow + tablero del equipo

### Tarea (Joel)

22D compró un Webflow y el diseñador (Jose) ya está diseñando sobre una plantilla comprada.
Existe un brandbook nuevo (`Sotsi and UHF Brand Guidelines.pdf`). Joel pidió un **plan de acción
para todo el equipo** (diseño, video, copy, imágenes) para migrar WordPress → Webflow, con
secciones a mantener/mejorar/quitar y **horas estimadas**, más un **tablero URL** que organice el
trabajo de todos. Decisiones: Fase 1 = sitio principal (blog después), horas **por rol**, tablero
estático **JSON-driven en GitHub Pages** (sin BD, sin backend).

### Contexto absorbido

- Leído el brandbook completo (48 págs) → destilado en `BRAND_REFERENCE.md` (dos marcas SOTSI
  navy/naturaleza + UHF purple/humanos; tokens de color; Canela/Jost; regla foto-real-no-IA).
- Inventario real extraído del reporte de auditoría → `data/site_inventory.json`:
  **110 páginas activas** (Main Site 22, Program/Event 43, Content 21, System 13, Thank You 11).

### Delegación a agentes (paralelo)

- **architect** → framework del plan: rúbrica de clasificación, veredicto para las 110 páginas,
  alcance Fase 1, benchmarks de horas por arquetipo, 5 sprints, Definition of Done, 8 riesgos.
- **code-architect** → arquitectura del tablero: esquema JSON, diseño del generador, UX, tokens CSS.

### Entregables producidos

| Archivo | Tipo | Qué es |
|---|---|---|
| `BRAND_REFERENCE.md` | new | Destilado operativo del brandbook para el equipo |
| `data/site_inventory.json` | new | Inventario real de 110 páginas por categoría |
| `seed_migration_plan.py` | new | Genera el plan desde el inventario + overrides de veredicto |
| `data/migration_plan.json` | new | **Fuente de verdad** editable: 110 págs con veredicto/sprint/horas/checklist |
| `build_migration_dashboard.py` | new | Genera el tablero de marca (KPIs, board Tabulator, slide-panel, guía) |
| `generate_migration_csv.py` | new | CSV de contenido + mapa de 301 redirects |
| `migration_dashboard.html` / `team.html` | generated | Tablero (publicar en GitHub Pages `/team`) |
| `SOTSI_Migration_Content.csv` | generated | 80 filas para el equipo de contenido |
| `SOTSI_Migration_Redirects.csv` | generated | 51 redirects 301 (drops + consolidate-losers) |
| `PLAN_MIGRACION_WEBFLOW.md` | new | **Documento guía maestro** (revisan Joel + Jose) |

### Números

- Veredictos: 13 REBUILD · 39 IMPROVE · 25 CONSOLIDATE · 3 KEEP · 30 DROP = 110.
- ~55 páginas construibles → **≈ 881.5 h** (Build 237.5 · Contenido 214 · Diseño 205 · Media 144 · Revisión 81).

### Cómo regenerar el tablero de migración

```bash
cd "/Users/joeldoradoaguilus/Documents/22D Marketing/SOTSI-WordPress-Audit"
# (opcional) re-seed desde el inventario si cambian los veredictos base:
python3 seed_migration_plan.py
# editar data/migration_plan.json (estatus, horas, checklist) y regenerar:
python3 build_migration_dashboard.py      # -> migration_dashboard.html + team.html
python3 generate_migration_csv.py         # -> CSVs de contenido + redirects
git add -A && git commit -m "update: migration plan" && git push   # live en ~1 min
```

### Pendiente (próxima sesión)

- [ ] Revisión Joel + Jose del plan y el board; confirmar veredictos sensibles (memorial Linda, DROPs).
- [ ] Decisión de commerce + membership (bloquea Sprint 3).
- [ ] Confirmar licencia de Canela; montar biblioteca de fotos reales (no IA).
- [ ] Publicar `team.html` en GitHub Pages y compartir URL. ✅ HECHO (live en `/team`).
- [ ] Fase 2: plan de migración del blog (187 posts, ya triados 167/20).

### Actualizaciones posteriores (mismo día)

**Tablero publicado.** `team.html` live en https://devreneceo.github.io/sotsi_wordpres_audit/team (commit 7b83e3a).

**Separación por grupos de prioridad** (commit 2922955). Se agregó el campo `group` a cada
página (`seed_migration_plan.py`): `principales` (15 págs, 247.5h — core must-have: home, about,
fundadores, books, get-started, events&programs, podcast, media, faqs, connect, newsletter, blog),
`programas` (59, 420.5h), `contenido` (22, 123.5h), `sistema` (14, 90h). El tablero ahora tiene
resumen por grupo, board agrupado y filtro de Grupo; el CSV de contenido incluye la columna `group`.

**Webflow MCP conectado a esta carpeta.** Se agregó el MCP de Webflow en **scope local** con
nombre propio **`webflow-sotsi`** (NO `webflow` genérico, que reusaba el OAuth de la carpeta UHF
por estar llaveado por nombre de servidor). Así SOTSI tiene su **propia cuenta/OAuth**, separada de
UHF. Pendiente: Joel hace `/mcp` → autoriza con la cuenta SOTSI (Chrome ya logueado) y reinicia
Claude Code para cargar las tools `mcp__webflow-sotsi__*`.
  - UHF/ → servidor `webflow` (cuenta A, intacta)
  - SOTSI-WordPress-Audit/ → servidor `webflow-sotsi` (cuenta B)
  - ⚠️ `/22D Marketing` (padre) tiene un Bearer token en texto plano — considerar migrar a OAuth / rotar.

### Pendiente real (próxima sesión)

- [ ] Completar OAuth de `webflow-sotsi` (`/mcp` + reinicio) y conectar el pipeline de contenido
      `migration_plan.json` → Webflow vía MCP, empezando por las Páginas principales.
- [ ] Revisión Joel + Jose del board; confirmar veredictos sensibles (memorial Linda, DROPs).
- [ ] Decisión de commerce + membership (bloquea Sprint 3).
- [ ] Confirmar licencia de Canela; montar biblioteca de fotos reales (no IA).
- [ ] Fase 2: plan de migración del blog (187 posts, ya triados 167/20) — Joel tiene dudas aquí.

---

## Session · 2026-05-25 (tarde) — Diagnóstico de la cuenta Webflow (MCP conectado)

### Contexto

Joel completó el OAuth de `webflow-sotsi` (`/mcp` → "Authentication successful. Connected to
webflow-sotsi") y pidió un **diagnóstico de qué hay actualmente en la cuenta Webflow** vía MCP,
para registrarlo aquí. Cuenta/workspace SOTSI: `workspaceId 69fb10a1d207c46d49542bb8`.

### Hallazgo: hay 3 sitios en el workspace

| # | Nombre | Site ID | Estado | Veredicto |
|---|---|---|---|---|
| 1 | Seat of the Soul Institute | `6a0421fefc0460de5474632a` | Creado 5/13, **nunca publicado**, 5 págs, 0 colecciones CMS | **Borrador IA — eliminar** |
| 2 | The Seat of the Soul Institute | `6a04240570c532ff7c8c12f1` | Creado 5/13, **nunca publicado**, 6 págs, 0 colecciones CMS | **Borrador IA — eliminar** |
| 3 | Seat of the Soul Institute | `6a0756563c0753689004ec7f` | Creado 5/15, **publicado 5/19**, 25 págs, 9 colecciones, screenshot | **EL REAL — sitio de trabajo de Jose** |

**Sitios 1 y 2** son borradores generados con el **AI Site Builder de Webflow** (el copy SEO ya es
real de SOTSI — Gary Zukav, "authentic power" — pero las páginas son genéricas: Home, Courses,
Membership, Books, About, Style guide; sin CMS). Recomendación: **borrarlos** para que nadie del
equipo abra la URL equivocada. Ambos siguen en subdominio webflow.io, sin dominio propio.

### Sitio 3 — el sitio real (plantilla "Shimma")

- Basado en **Shimma**, plantilla de Webflow e-commerce para estudios de **yoga / Pilates /
  wellness**. Timezone `Asia/Dhaka` (autor de la plantilla / contratista).
- **Publicado 5/19** solo a subdominio `webflow.io` — **sin dominio propio** (`customDomains: []`).
- Locale primario English, **`enabled:false`** (localización apagada). Sin Google Tag, sin data
  collection.
- Screenshot del 5/19: `https://screenshots.webflow.com/sites/6a0756563c0753689004ec7f/20260519134458_e5019552e1e191841e5381d0b030ff24.png`

**25 páginas:** Home · About · Classes · Events · Blog · Contact Us · Team · Products · Checkout ·
Checkout (PayPal) · Order Confirmation · 404 · Password(401) · utility-pages (Style Guide, License,
Changelog) · plantillas CMS (Blogs, Events, Classes, Teams, Products, Categories, SKUs, **Courses**,
**Testimonials**).

**9 colecciones CMS:** Classes · Events · **Blogs** · Teams · Categories · SKUs · Products ·
**Courses** (nueva, 5/22) · **Testimonials** (nueva, 5/22).

**Trabajo reciente de Jose (5/22):** creó las colecciones + páginas plantilla **Courses** y
**Testimonials**, y editó About, Contact, Team, Blog, Events, Classes, Home. Está adaptando la
plantilla, todavía no migrando contenido.

**⚠️ Pendientes de plantilla (todo default Shimma):**
- Todos los `<title>` SEO siguen diciendo **"… - Shimma - Webflow Ecommerce Website Template"** →
  reemplazo global pendiente.
- El **Blog tiene solo 4 posts demo** con texto lorem ("Robert Fox" como autor, cuerpo de
  "task-management app", contenido falso de jardinería/yoga). Cero contenido real de SOTSI aún.

### Esquema de la colección "Blogs" (clave para migrar los 187 posts)

Collection ID `6a0756583c0753689004ee1a`. Campos actuales:

| Campo (slug) | Tipo | Mapea desde WordPress |
|---|---|---|
| `name` (Blog Title, **req**) | PlainText (max 256) | título del post |
| `slug` (**req**) | PlainText | slug del post |
| `short-description` | PlainText 1-línea | excerpt |
| `blog-image` | Image | thumbnail / featured image |
| `blog-banner-image` | Image | hero del detalle |
| `editor-name` | PlainText | autor |
| `editor-image` | Image | avatar del autor |
| `category-name` | PlainText | ⚠️ texto libre, **NO** referencia a Categories — serie (Soul Snack/Feast/Seed/Wisdom Wed) |
| `blog-single-description` | PlainText | descripción secundaria del detalle |
| `blog-rich-text` | RichText | **cuerpo del post** (`content.rendered`) |

**Faltan campos que el contenido SOTSI necesita** (decisión para Jose antes de importar):
1. **`published-on` (DateTime)** — no hay campo de fecha; el orden/archivo del blog por fecha no
   funcionará sin esto. *Crítico para 187 posts ordenados por fecha.*
2. **`seo-description` (PlainText)** — no hay meta description por item; los SEO quick-wins del CSV
   (166/167 sin meta) no tienen dónde aterrizar todavía.
3. (Opcional) **`source-url`** — para construir los 301 redirects WP→Webflow por post.
4. (Opcional) Convertir `category-name` a **referencia** a una colección de Series/Categorías si se
   quiere filtrado relacional; con texto libre basta para empezar.

### Implicaciones para el plan de migración

- El pipeline `data/posts_extracted.json` (187 posts triados: 167 keep / 20 drop) ya tiene
  título, slug, excerpt, cuerpo, categoría, autor, fecha y stats SEO → mapea casi 1:1 a esta
  colección **una vez se agreguen los 2 campos faltantes** (`published-on`, `seo-description`).
- La importación se puede automatizar vía `data_cms_tool > create_collection_items` (lotes), pero
  **primero** hay que: (a) decidir campos, (b) subir imágenes destacadas como assets Webflow,
  (c) limpiar el RichText de WP (clases/IDs de Yoast) al formato RichText de Webflow.
- Las imágenes de los posts hoy viven en `seatofthesoul.com` (WP). Webflow no las descarga solo;
  hay que subirlas con `asset_tool > upload_image_by_url` y reescribir los `src` del RichText.

### Acciones recomendadas (próxima sesión, en orden)

1. **Limpieza:** borrar sitios 1 y 2 (borradores IA) — confirmar con Joel primero.
2. **Jose:** reemplazar títulos SEO "Shimma…" y borrar los 4 posts demo del blog.
3. **Decidir el esquema final de Blogs** (agregar `published-on` + `seo-description` mínimo).
4. **Piloto de import:** migrar 3–5 posts reales vía MCP de extremo a extremo (assets + RichText +
   campos) para validar el pipeline antes de los 187.
5. Confirmar **dominio propio** (seatofthesoul.com) y plan de 301 redirects (`SOTSI_Migration_Redirects.csv`).

---

## Session · 2026-05-25 (noche) — Tablero v2: i18n, "ver vieja", Plan de Home

### Tarea (Joel)

Sobre el tablero `/team`: (1) botón por página para ver la URL vieja de WordPress; (2) toggle de
idioma ES/EN; (3) **Plan de acción por página, empezando SOLO por Home** — mini-dashboard admin que
mapea las secciones del Home original (WordPress) → Webflow con checkboxes, horas y notas; (4)
análisis del template **Shimma** (estructura/componentes globales/tokens) y mapeo del Home contra
el template; (5) bloque "Contexto de Home por IA" con recomendación estructural.

### Investigación (2 agentes en paralelo)

- **Home WordPress** (`seatofthesoul.com/`): 10 secciones reales + nav + footer. Hallazgos: `/home`
  hace **301 → `/`** (raíz canónica, WP page 41); el hero es un **carrusel Swiper de 4 slides**;
  hay **spam de casino inyectado** (señal de WP hackeado — limpiar, no migrar); el botón "ENROLL IN
  A COURSE" no tiene destino; la comunidad se empuja **2 veces** (CTAs duplicados a Mighty Networks);
  el "Final CTA" dice 'Start your journey' pero apunta al newsletter.
- **Template Shimma** (`shimma.webflow.io`): 10 secciones + librería de ~17 bloques reusables
  (video-hero, about-split, cards de oferta, team grid, testimonial slider, stats band, marquee CTA
  global, etc.). Tokens del template: Playfair Display + Montserrat sobre crema/arena/espresso/cobre,
  botones pill — **requiere re-skin** a navy/Canela. Nav con mega-menú + **carrito ecommerce** +
  CTA "Get Template" + créditos Flowzai → reescribir/apagar.

### Arquitectura del tablero (refactor)

El builder pasó de fragmentos Python a **shell + datos + assets inyectados**, con el render
dinámico e i18n movidos a JS (para que ES/EN sea uniforme). Archivos nuevos:

| Archivo | Qué es |
|---|---|
| `dashboard_src/styles.css` | Todo el CSS (base + toggle idioma, botón "ver vieja", modal de plan, tabla de secciones, tarjeta IA) |
| `dashboard_src/app.js` | Cliente: diccionario i18n ES/EN, `computeMeta`, render de KPIs/sprints/grupos/guía, board Tabulator, slide-panel, **modal de Plan de página** |
| `data/page_plans.json` | **Plan por página, indexado por slug** (reutilizable). Hoy: `home` con 13 secciones + `ai_context` + `template_analysis`. Agregar una página nueva = añadir una key |
| `build_migration_dashboard.py` | Reescrito: carga `migration_plan.json` + `page_plans.json`, inyecta CSS/JS/datos, escribe `migration_dashboard.html` + `team.html` |

### Funcionalidades entregadas

1. **Botón "Ver" por página** (columna en el board, abre la URL vieja de WP en pestaña nueva;
   `stopPropagation` para no abrir el panel) + botón "Ver página vieja ↗" en el slide-panel.
2. **Toggle ES/EN** (arriba-derecha, persiste en `localStorage`). Traduce toda la UI: header, tabs,
   KPIs, filtros, columnas del board, panel, modal y guía. El contenido-dato (notas, labels de
   sprint, veredicto del plan) queda en su idioma de autoría.
3. **Plan de Home** (modal mini-dashboard admin): tira de horas (12·6·8·12·4 = **42h**), tabla de
   13 secciones con columnas **Sección · Esqueleto viejo (WP) · Esqueleto nuevo (Webflow) · Acción
   (reconstruir/mejorar/consolidar/agregar/quitar) · Mapeado a Webflow · Notas · Horas · check**.
   Checkboxes con persistencia local (nota: para el equipo se edita el JSON y se regenera). Punto
   dorado en el board marca las páginas que ya tienen plan; se abre desde el panel o desde la tarjeta
   "Planes de página" del Resumen.
4. **Análisis del template Shimma** dentro del modal: componentes globales, bloques reusables (chips),
   qué quitar/arreglar, y nota de re-skin de tokens.
5. **Contexto de Home por IA**: tarjeta con veredicto ("RECONSTRUIR sobre Shimma, 10→8 secciones +
   limpieza de deuda") + resumen + 6 recomendaciones concretas.

### Mapeo Home WordPress → Shimma (resumen del plan)

Hero carrusel→**video-hero** (reconstruir, 1 mensaje ancla) · Value prop→about-split (mejorar) ·
Tools promo→**consolidar** en el CTA del intro · 4 pilares→cards de oferta CMS (reconstruir, arreglar
link roto) · Join Gary→evento (mejorar) · 2 bandas de comunidad→**1 sola** (consolidar) · Books→
about-split (mejorar) · Founders→team-grid (reconstruir, fotos reales) · Final CTA→marquee global
(mejorar) · +**agregar** testimonials / stats / latest-blog del template · **quitar** spam de casino.

### Verificación

`node --check` del JS OK. Render headless (Chrome) confirma: 5 KPIs, 5 sprints, grupos 14/42/18/6,
guía, board con 110 filas + botón "Ver", toggle EN traduce todo, modal con 13 secciones + IA +
Shimma, **sin `NaN`/`undefined`**. Tabla del plan con scroll horizontal en móvil.

### Cómo regenerar

```bash
cd "/Users/joeldoradoaguilus/Documents/22D Marketing/SOTSI-WordPress-Audit"
# editar data/migration_plan.json (páginas) y/o data/page_plans.json (planes por sección)
python3 build_migration_dashboard.py     # -> migration_dashboard.html + team.html
git add -A && git commit -m "feat: dashboard v2" && git push   # live en /team ~1 min
```

### Pendiente

- [ ] Revisión de Joel + Jose del Plan de Home (veredictos por sección, horas, mapeo a Shimma).
- [ ] Publicar (push) para que `/team` muestre la v2.
- [ ] Replicar el patrón de plan para la siguiente página principal (About / Fundadores).
- [ ] Confirmar decisión de commerce/membership (afecta secciones 4 pilares, books, comunidad).
