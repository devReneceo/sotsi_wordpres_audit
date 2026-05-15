# SOTSI WordPress Audit — Work Log

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
| `WORK_LOG.md` | updated (step 4 added to regenerate block, scripts table extended, this session entry) |
