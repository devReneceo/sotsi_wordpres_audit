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
