# SOTSI WordPress Audit — Work Log

**Site:** seatofthesoul.com  
**Repo:** devReneceo/sotsi_wordpres_audit  
**Tool:** audit_sotsi.py — generates SOTSI_Audit_Report.html

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

## Session · 2026-05-13 — Blog Migration Triage (Sprint 1: machote MD)

### Task: Christopher asked for a triage of all old blog posts — flag dated/event content that should NOT migrate to the new SOTSI site, rate the rest, and add SEO suggestions.

### Architecture decision

- **No paid API calls.** Joel uses the Claude monthly plan ($100/mo), not the Anthropic API. So:
  - Python does ALL the heavy lifting (REST API fetch, HTML parsing, heuristics, classification).
  - Token cost minimized — Claude only reads what Python flags as ambiguous.
  - Zero `ANTHROPIC_API_KEY` in the repo; no `anthropic` SDK dependency.

### Sprint 1 deliverable: `BLOG_MIGRATION_TRIAGE.md`

New script `extract_blog_data.py` (stdlib-only, zero pip deps):

- Fetches every published blog post from `/wp-json/wp/v2/posts` with `content.rendered`, `excerpt`, `categories`, `yoast_head_json`.
- Resolves WP category IDs to names via `/wp-json/wp/v2/categories`.
- Parses each post body with stdlib `html.parser` to count: headings (H1–H4), images + missing alts, internal/external links, word count.
- Applies deterministic heuristics:
  1. **WP category `Exclude` → `auto_drop`** (the SOTSI team already pre-tagged these in WordPress).
  2. **Slug matches `soul-snack-*` / `soul-feast-*` / `soul-seed-*` / `wisdom-wednesday-*` → `auto_keep`** (evergreen series).
  3. Event-keyword detection (`register`, `Zoom`, `RSVP`, `tickets`, `webinar`, `early bird`, etc.) and past-year regex for the remaining posts.
- Generates:
  - `data/posts_extracted.json` — structured payload (187 posts).
  - `BLOG_MIGRATION_TRIAGE.md` — human-readable triage report (~4,000 lines) grouped into Section A (drop), B (keep), C/D (manual review — empty in this run).

### Results

| Bucket | Posts | Notes |
|---|---:|---|
| **DROP** (Section A) | **20** | All `Exclude`-tagged in WP — confirmed by Christopher's team |
| **KEEP** (Section B) | **167** | Soul Snacks/Feasts/Seeds/Wisdom Wednesdays |
| Manual review (Section C/D) | **0** | All posts resolved by rules — no AI tokens spent on per-post review |

**Total:** 187 published posts (site grew from 166 since April 30 audit).

### QA validation

- Spot-checked 19 evergreen posts that triggered "registration CTA" / "enrollment CTA" keyword hits.
- Confirmed: all hits are the same boilerplate footer ("Enroll in Soul Themes Today") — Soul Themes is a permanent program, not an expired event. Correctly classified as KEEP.

### Next sprint (Sprint 2 — UI/UX)

Convert `BLOG_MIGRATION_TRIAGE.md` into a new dynamic tab inside the existing audit reporter (`SOTSI_Audit_Report.html`). Likely tab name: **"Blog Migration Triage"**. Same Tabulator + slide-panel UX as the existing tabs.

### To regenerate

```bash
cd "/Users/joeldoradoaguilus/Documents/22D Marketing/SOTSI-WordPress-Audit"
python3 extract_blog_data.py
# outputs: data/posts_extracted.json + BLOG_MIGRATION_TRIAGE.md
```

Run takes ~5–10 seconds. No API key required.
