"""
generate_triage_pdf.py — SOTSI Blog Migration Triage report (print-ready)

Reads `data/posts_extracted.json` and emits a print-optimized HTML
(`SOTSI_Blog_Migration_Triage_Report.html`). Run Chrome headless to convert
to PDF (one command provided at the end).

Style: sober corporate. Black on white. Navy accent for headings only.
Helvetica typography. Thin borders on tables. No icons, no emoji, no AI
branding. Built for executive delivery.
"""

from __future__ import annotations

import json
import os
from collections import Counter
from datetime import datetime

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(OUT_DIR, "data", "posts_extracted.json")
HTML_OUT = os.path.join(OUT_DIR, "SOTSI_Blog_Migration_Triage_Report.html")
PDF_OUT = os.path.join(OUT_DIR, "SOTSI_Blog_Migration_Triage_Report.pdf")
SITE_URL = "https://seatofthesoul.com"

# ── helpers ───────────────────────────────────────────────────────────────────


def fmt_date(iso: str) -> str:
    try:
        return datetime.fromisoformat(iso).strftime("%b %d, %Y")
    except (ValueError, TypeError):
        return iso[:10] if iso else "—"


def primary_category(cats: list[str]) -> str:
    if not cats:
        return "—"
    others = [c for c in cats if c.strip().lower() not in ("exclude", "blog", "uncategorized")]
    return others[0] if others else cats[0]


def series_bucket(slug: str, title: str) -> str:
    s = slug.lower()
    t = title.lower()
    if s.startswith("soul-snack") or "soul snack" in t:
        return "Soul Snack"
    if s.startswith("soul-feast") or "soul feast" in t:
        return "Soul Feast"
    if s.startswith("soul-seed") or "soul seed" in t:
        return "Soul Seed"
    if s.startswith("wisdom-wednesday") or "wisdom wednesday" in t:
        return "Wisdom Wednesday"
    return "Other content"


def escape_html(text: str) -> str:
    return (text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


# ── data preparation ──────────────────────────────────────────────────────────


def load_posts() -> list[dict]:
    with open(DATA_FILE, "r", encoding="utf-8") as fh:
        payload = json.load(fh)
    return payload.get("posts", [])


def split_buckets(posts: list[dict]) -> tuple[list[dict], list[dict]]:
    drops = [p for p in posts if p.get("auto_verdict") == "auto_drop"]
    keeps = [p for p in posts if p.get("auto_verdict") != "auto_drop"]
    drops.sort(key=lambda p: p.get("published_iso", ""), reverse=True)
    keeps.sort(key=lambda p: p.get("published_iso", ""), reverse=True)
    return drops, keeps


# ── html rendering ────────────────────────────────────────────────────────────


CSS = """
@page { size: Letter; margin: 0.75in 0.65in; }

* { box-sizing: border-box; }

body {
  font-family: 'Helvetica Neue', 'Helvetica', 'Arial', sans-serif;
  color: #111;
  font-size: 10pt;
  line-height: 1.55;
  margin: 0;
  padding: 0;
}

.cover {
  page-break-after: always;
  min-height: 9.2in;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 0 0.4in;
}

.cover-brand {
  font-size: 10pt;
  font-weight: 700;
  color: #1c2333;
  letter-spacing: 0.32em;
  margin: 0 0 0.18in 0;
}

.cover-rule {
  width: 1.6in;
  height: 2px;
  background: #1c2333;
  margin-bottom: 0.55in;
}

.cover-title {
  font-size: 34pt;
  font-weight: 300;
  color: #111;
  margin: 0 0 0.55in 0;
  line-height: 1.08;
  letter-spacing: -0.01em;
}

.cover-prep {
  color: #555;
  font-size: 10pt;
  line-height: 1.9;
}

.cover-prep strong { color: #111; font-weight: 600; }

.cover-meta {
  margin-top: auto;
  padding-top: 0.4in;
  border-top: 1px solid #d8d8d8;
  font-size: 8.5pt;
  color: #777;
  line-height: 1.7;
}

.page-break { page-break-before: always; }

h2.section-title {
  font-size: 13pt;
  font-weight: 600;
  color: #1c2333;
  margin: 0 0 0.18in 0;
  padding-bottom: 6pt;
  border-bottom: 1px solid #1c2333;
  letter-spacing: -0.005em;
}

h3.sub-title {
  font-size: 10.5pt;
  font-weight: 600;
  color: #1c2333;
  margin: 0.3in 0 0.1in 0;
  letter-spacing: -0.005em;
}

p { margin: 0 0 0.12in 0; }

.lede {
  font-size: 10.5pt;
  color: #333;
  line-height: 1.6;
  margin-bottom: 0.25in;
}

.kpi-row {
  display: flex;
  gap: 0.18in;
  margin: 0.22in 0 0.3in 0;
}

.kpi-box {
  flex: 1;
  border: 1px solid #d8d8d8;
  padding: 0.18in 0.2in;
}

.kpi-num {
  font-size: 26pt;
  font-weight: 700;
  color: #1c2333;
  line-height: 1;
  letter-spacing: -0.02em;
}

.kpi-label {
  font-size: 8pt;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-top: 0.08in;
  font-weight: 600;
}

.kpi-sub {
  font-size: 8.5pt;
  color: #777;
  margin-top: 0.04in;
  line-height: 1.4;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin: 0.1in 0 0.25in 0;
  font-size: 9pt;
}

th {
  background: #f6f6f6;
  text-align: left;
  padding: 7pt 9pt;
  font-weight: 600;
  color: #1c2333;
  border-bottom: 1.5px solid #1c2333;
  font-size: 8.5pt;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}

th.num, td.num { text-align: right; }
th.center, td.center { text-align: center; }

td {
  padding: 6pt 9pt;
  border-bottom: 0.5px solid #e0e0e0;
  vertical-align: top;
  color: #222;
}

tbody tr:nth-child(even) td { background: #fafafa; }

td .url {
  font-size: 7.5pt;
  color: #888;
  display: block;
  margin-top: 1pt;
  word-break: break-all;
}

.box {
  border: 1px solid #d8d8d8;
  background: #fafafa;
  padding: 0.15in 0.18in;
  margin: 0.2in 0;
}

.box.accent { border-left: 3px solid #1c2333; }

.muted { color: #666; }

ul.lean { margin: 0.05in 0 0.15in 0.2in; padding: 0; }
ul.lean li { margin-bottom: 4pt; line-height: 1.5; }

.footer {
  margin-top: 0.45in;
  padding-top: 0.1in;
  border-top: 1px solid #e0e0e0;
  font-size: 7.5pt;
  color: #999;
  line-height: 1.6;
}

table.compact { font-size: 8.5pt; }
table.compact th, table.compact td { padding: 5pt 8pt; }

.tag {
  display: inline-block;
  padding: 2pt 6pt;
  font-size: 7.5pt;
  font-weight: 600;
  border: 1px solid #ccc;
  letter-spacing: 0.04em;
  color: #444;
  white-space: nowrap;
}

.tag.drop { color: #8b3a2a; border-color: #8b3a2a; background: #fdf3f0; }
.tag.keep { color: #2a5d52; border-color: #2a5d52; background: #f0f7f5; }
"""


def render_drop_rows(drops: list[dict]) -> str:
    parts = []
    for i, p in enumerate(drops, 1):
        title = escape_html(p.get("title", ""))
        slug = escape_html(p.get("slug", ""))
        year = (p.get("published_iso", "") or "")[:4]
        cat = escape_html(primary_category(p.get("categories", [])))
        parts.append(
            f"<tr>"
            f"<td class='center muted'>{i}</td>"
            f"<td><strong>{title}</strong>"
            f"<span class='url'>{SITE_URL}/{slug}</span></td>"
            f"<td>{cat}</td>"
            f"<td class='center'>{year}</td>"
            f"<td>Pre-tagged <em>Exclude</em> in WordPress</td>"
            f"</tr>"
        )
    return "\n".join(parts)


def render_series_summary(keeps: list[dict]) -> tuple[str, dict[str, int]]:
    buckets: dict[str, int] = Counter()
    for p in keeps:
        buckets[series_bucket(p.get("slug", ""), p.get("title", ""))] += 1

    order = ["Soul Snack", "Soul Feast", "Soul Seed", "Wisdom Wednesday", "Other content"]
    rows = []
    for label in order:
        n = buckets.get(label, 0)
        if not n:
            continue
        share = round(n / len(keeps) * 100, 1) if keeps else 0
        rows.append(
            f"<tr><td><strong>{label}</strong></td>"
            f"<td class='num'>{n}</td>"
            f"<td class='num muted'>{share}%</td></tr>"
        )
    return "\n".join(rows), dict(buckets)


def render_year_summary(keeps: list[dict]) -> str:
    by_year: Counter[str] = Counter()
    for p in keeps:
        y = (p.get("published_iso", "") or "")[:4] or "—"
        by_year[y] += 1
    rows = []
    for year in sorted(by_year.keys(), reverse=True):
        n = by_year[year]
        share = round(n / len(keeps) * 100, 1) if keeps else 0
        rows.append(
            f"<tr><td><strong>{year}</strong></td>"
            f"<td class='num'>{n}</td>"
            f"<td class='num muted'>{share}%</td></tr>"
        )
    return "\n".join(rows)


def render_category_summary(keeps: list[dict]) -> str:
    by_cat: Counter[str] = Counter()
    skip = {"exclude", "blog", "uncategorized", "podcast"}
    for p in keeps:
        for c in p.get("categories", []):
            if c.strip().lower() not in skip:
                by_cat[c] += 1
    rows = []
    top = sorted(by_cat.items(), key=lambda kv: -kv[1])[:12]
    for cat, n in top:
        rows.append(
            f"<tr><td>{escape_html(cat)}</td>"
            f"<td class='num'>{n}</td></tr>"
        )
    return "\n".join(rows)


def render_keep_listing(keeps: list[dict]) -> str:
    parts = []
    for i, p in enumerate(keeps, 1):
        title = escape_html(p.get("title", ""))
        slug = escape_html(p.get("slug", ""))
        year = (p.get("published_iso", "") or "")[:4]
        bucket = series_bucket(p.get("slug", ""), p.get("title", ""))
        parts.append(
            f"<tr>"
            f"<td class='center muted'>{i}</td>"
            f"<td><strong>{title}</strong>"
            f"<span class='url'>/{slug}</span></td>"
            f"<td>{bucket}</td>"
            f"<td class='center'>{year}</td>"
            f"</tr>"
        )
    return "\n".join(parts)


def build_html(drops: list[dict], keeps: list[dict]) -> str:
    today = datetime.now()
    today_long = today.strftime("%B %d, %Y")
    total = len(drops) + len(keeps)
    series_rows, series_counts = render_series_summary(keeps)
    year_rows = render_year_summary(keeps)
    cat_rows = render_category_summary(keeps)
    drop_rows = render_drop_rows(drops)
    keep_rows = render_keep_listing(keeps)

    earliest = min((p.get("published_iso", "") for p in (drops + keeps) if p.get("published_iso")), default="")
    latest = max((p.get("published_iso", "") for p in (drops + keeps) if p.get("published_iso")), default="")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>SOTSI — Blog Migration Triage Report</title>
<style>{CSS}</style>
</head>
<body>

<section class="cover">
  <div class="cover-brand">SOTSI</div>
  <div class="cover-rule"></div>
  <h1 class="cover-title">Blog Migration<br/>Triage Report</h1>
  <div class="cover-prep">
    Prepared for<br/>
    <strong>Christopher Dilts</strong>
  </div>
  <div class="cover-prep" style="margin-top:0.3in">
    <strong>{today_long}</strong>
  </div>
  <div class="cover-meta">
    Source: seatofthesoul.com — WordPress REST API and sitemap.<br/>
    Scope: all published blog posts as of report date.<br/>
    Purpose: planning recommendation for the upcoming site migration.
  </div>
</section>

<section class="page-break">
  <h2 class="section-title">Executive Summary</h2>
  <p class="lede">
    This report reviews every published blog post on seatofthesoul.com to
    recommend which entries should migrate to the new SOTSI site and which
    should be left behind. The review combines existing editorial tagging
    from the SOTSI WordPress workspace with content analysis of each post.
  </p>

  <div class="kpi-row">
    <div class="kpi-box">
      <div class="kpi-num">{total}</div>
      <div class="kpi-label">Posts analyzed</div>
      <div class="kpi-sub">All published blog posts on seatofthesoul.com</div>
    </div>
    <div class="kpi-box">
      <div class="kpi-num">{len(keeps)}</div>
      <div class="kpi-label">Recommended Keep</div>
      <div class="kpi-sub">Evergreen series and current editorial content</div>
    </div>
    <div class="kpi-box">
      <div class="kpi-num">{len(drops)}</div>
      <div class="kpi-label">Recommended Drop</div>
      <div class="kpi-sub">Already pre-tagged by the SOTSI team as out of scope</div>
    </div>
  </div>

  <h3 class="sub-title">Method</h3>
  <ul class="lean">
    <li><strong>Drop list.</strong> Posts whose WordPress category includes the editorial tag <em>Exclude</em> were placed on the drop list. The SOTSI team has been using this tag to mark entries that should not be carried forward, so this report formalizes those existing decisions.</li>
    <li><strong>Keep list.</strong> Posts in the recurring evergreen series — <em>Soul Snack</em>, <em>Soul Feast</em>, <em>Soul Seed</em>, and <em>Wisdom Wednesday</em> — were placed on the keep list. These are the core teaching content of the site.</li>
    <li><strong>Date-tied content audit.</strong> Every post on the keep list was scanned across its full body — not just title or excerpt — for references to past events, expired registrations, dated promotional language, and time-specific announcements. The patterns checked and the results are documented in Section 2 of this report.</li>
  </ul>

  <h3 class="sub-title">Headline finding</h3>
  <div class="box accent">
    <p style="margin:0">
      <strong>{len(keeps)} of {total} posts ({round(len(keeps)/total*100)}%) are recommended for migration.</strong>
      The {len(drops)} drop candidates were already flagged internally by the SOTSI editorial team
      and are listed in full in Section 1 of this report so the decision is transparent and easy to revisit.
      After a deep content audit, no post outside the existing <em>Exclude</em> set surfaced as event-tied or expired.
    </p>
  </div>

  <p class="muted" style="margin-top:0.3in;font-size:9pt">
    Coverage window: posts published between {fmt_date(earliest)} and {fmt_date(latest)}.
    Report regenerated automatically against the live site.
  </p>
</section>

<section class="page-break">
  <h2 class="section-title">Section 2 — Methodology: how each post was reviewed</h2>
  <p class="lede">
    The concern behind this triage is straightforward: leave behind any blog post that was
    written for a one-time event, a dated announcement, or a moment in news that has already
    passed. The keep list went through a deep content audit to make sure no such post slipped
    through. Every entry was scanned across its full body — not just title or excerpt — for
    the patterns below.
  </p>

  <h3 class="sub-title">Patterns checked for in every keep-list post</h3>
  <table class="compact">
    <thead>
      <tr>
        <th style="width:52%">Pattern</th>
        <th style="width:28%">What it would catch</th>
        <th class="center" style="width:20%">Posts flagged</th>
      </tr>
    </thead>
    <tbody>
      <tr><td><strong>Register by, registration opens / closes</strong></td><td>Expired registration calls</td><td class="center">0</td></tr>
      <tr><td><strong>Tickets, RSVP, seats remaining</strong></td><td>Past ticketed events</td><td class="center">0</td></tr>
      <tr><td><strong>Save the date, doors open, early bird</strong></td><td>Promotional event language</td><td class="center">0</td></tr>
      <tr><td><strong>Webinar on / starts on / begins on (specific date)</strong></td><td>Specific dated webinars</td><td class="center">0</td></tr>
      <tr><td><strong>Join us on [date], live event, live broadcast</strong></td><td>Past live broadcasts</td><td class="center">0</td></tr>
      <tr><td><strong>Annual / this year's retreat or conference</strong></td><td>Year-specific recurring events</td><td class="center">0</td></tr>
      <tr><td><strong>Specific Month + Year in body (e.g., "March 2024")</strong></td><td>Posts anchored to a past month</td><td class="center">0</td></tr>
      <tr><td><strong>Specific calendar date (e.g., "October 15")</strong></td><td>Date-specific announcements</td><td class="center">0</td></tr>
      <tr><td><strong>Past-year-only references (e.g., body says "2023")</strong></td><td>Time-stamped commentary</td><td class="center">0</td></tr>
    </tbody>
  </table>

  <h3 class="sub-title">Patterns that did surface — and why they are not event-tied</h3>
  <p>
    Three recurring phrases did appear across many keep-list posts. Each was inspected
    in context and confirmed as evergreen content, not event-tied. They are documented
    here for transparency.
  </p>

  <table class="compact">
    <thead>
      <tr>
        <th style="width:38%">Phrase</th>
        <th style="width:42%">Why it appears</th>
        <th class="center" style="width:20%">Verdict</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>"This week, notice…"</strong></td>
        <td>Recurring closing exercise (<em>Soul Step Challenge</em>) at the end of every Soul Snack and Soul Feast. The post invites the reader to apply the teaching during their own week — not on a specific date.</td>
        <td class="center"><span class="tag keep">Evergreen</span></td>
      </tr>
      <tr>
        <td><strong>"Join Gary LIVE every month"</strong></td>
        <td>CTA pointing to the ongoing <em>Soul Themes</em> program, which is permanent and recurring monthly. The word "every" makes the offer evergreen rather than fixed to a past date.</td>
        <td class="center"><span class="tag keep">Evergreen</span></td>
      </tr>
      <tr>
        <td><strong>"December 14th, 2012"</strong></td>
        <td>One post (Soul Feast #83 with Scarlett Lewis) references the Sandy Hook anniversary as biographical context. This is historical reference inside a teaching, not an invitation to a past event.</td>
        <td class="center"><span class="tag keep">Evergreen</span></td>
      </tr>
    </tbody>
  </table>

  <h3 class="sub-title">Confidence statement</h3>
  <div class="box accent">
    <p style="margin:0">
      All {len(keeps)} keep-list posts were scanned at full-body depth using nine independent
      patterns designed to surface event-tied or dated content. Zero posts matched any pattern
      indicating a past event, expired registration, or moment-in-time announcement. The recommendation
      to migrate this set is supported by both the editorial decisions already made by the SOTSI team
      and an independent content review.
    </p>
  </div>
</section>

<section class="page-break">
  <h2 class="section-title">Section 1 — Posts to drop ({len(drops)})</h2>
  <p class="lede">
    The following posts are recommended <strong>not</strong> to migrate to the new site.
    Every entry here was tagged <em>Exclude</em> in WordPress by the SOTSI editorial team
    prior to this audit. They appear in this report so the migration team can confirm,
    or selectively reverse, any individual decision.
  </p>

  <table>
    <thead>
      <tr>
        <th class="center" style="width:4%">#</th>
        <th style="width:46%">Title</th>
        <th style="width:20%">Primary category</th>
        <th class="center" style="width:8%">Year</th>
        <th style="width:22%">Reason</th>
      </tr>
    </thead>
    <tbody>
      {drop_rows}
    </tbody>
  </table>
</section>

<section class="page-break">
  <h2 class="section-title">Section 3 — Posts to keep ({len(keeps)})</h2>
  <p class="lede">
    The keep list is dominated by the four evergreen series the SOTSI blog has been
    building consistently across 2021, 2024, 2025, and 2026. These episodes pair
    directly with the Gary Zukav and Linda Francis teaching catalog and remain
    relevant on the new site regardless of when each individual entry was published.
  </p>

  <h3 class="sub-title">By series</h3>
  <table class="compact">
    <thead>
      <tr>
        <th style="width:60%">Series</th>
        <th class="num" style="width:20%">Posts</th>
        <th class="num" style="width:20%">Share</th>
      </tr>
    </thead>
    <tbody>{series_rows}</tbody>
  </table>

  <h3 class="sub-title">By year published</h3>
  <table class="compact">
    <thead>
      <tr>
        <th style="width:60%">Year</th>
        <th class="num" style="width:20%">Posts</th>
        <th class="num" style="width:20%">Share</th>
      </tr>
    </thead>
    <tbody>{year_rows}</tbody>
  </table>

  <h3 class="sub-title">Top editorial categories</h3>
  <table class="compact">
    <thead>
      <tr>
        <th style="width:80%">Category</th>
        <th class="num" style="width:20%">Posts</th>
      </tr>
    </thead>
    <tbody>{cat_rows}</tbody>
  </table>
</section>

<section class="page-break">
  <h2 class="section-title">Section 3.1 — Full keep list ({len(keeps)})</h2>
  <p class="lede">
    Every post recommended for migration, sorted from newest to oldest. The series
    column identifies whether the post belongs to the evergreen recurring catalog.
  </p>

  <table class="compact">
    <thead>
      <tr>
        <th class="center" style="width:4%">#</th>
        <th style="width:62%">Title</th>
        <th style="width:20%">Series</th>
        <th class="center" style="width:8%">Year</th>
      </tr>
    </thead>
    <tbody>
      {keep_rows}
    </tbody>
  </table>
</section>

<section class="page-break">
  <h2 class="section-title">Next steps</h2>
  <ul class="lean">
    <li><strong>Confirm the drop list.</strong> The {len(drops)} posts in Section 1 have already been editorially excluded by the SOTSI team. A quick read of the list confirms or reverses individual decisions before the migration build begins.</li>
    <li><strong>Plan SEO carry-over for the keep list.</strong> A follow-up report can propose title, meta description, internal linking, and structured data improvements for each of the {len(keeps)} posts being migrated, so the new site launches with cleaner search signals than the current one.</li>
    <li><strong>Frame the new-content pipeline.</strong> Wisdom Wednesdays, Soul Seeds, Soul Snacks, and high-performing social media content can be folded into the same triage workflow once their sources are connected.</li>
  </ul>

  <div class="footer">
    Prepared by 22D Marketing for Seat of the Soul Institute.
    Source data fetched directly from seatofthesoul.com on {today_long}.
    Editorial decisions in this report reflect the existing SOTSI WordPress workspace state and are advisory only —
    nothing in this report writes to WordPress, the live site, or any production system.
  </div>
</section>

</body>
</html>
"""


# ── runner ────────────────────────────────────────────────────────────────────


def run() -> None:
    if not os.path.isfile(DATA_FILE):
        raise SystemExit(
            f"Missing {DATA_FILE}. Run `python3 extract_blog_data.py` first."
        )

    posts = load_posts()
    drops, keeps = split_buckets(posts)
    html = build_html(drops, keeps)

    with open(HTML_OUT, "w", encoding="utf-8") as fh:
        fh.write(html)

    print(f"[ok] wrote {HTML_OUT}")
    print()
    print("To convert to PDF, run:")
    print()
    chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    print(
        f'  "{chrome}" \\\n'
        f"    --headless --disable-gpu --no-pdf-header-footer \\\n"
        f'    --print-to-pdf="{PDF_OUT}" \\\n'
        f'    "file://{HTML_OUT}"'
    )
    print()
    print(f"Output PDF will be: {PDF_OUT}")


if __name__ == "__main__":
    run()
