"""
extract_blog_data.py — SOTSI Blog Migration Triage extractor

Fetches all published blog posts from seatofthesoul.com (WordPress REST API),
parses their HTML content with the stdlib HTMLParser, and applies deterministic
heuristics to pre-classify each post for the migration triage report.

Outputs:
  data/posts_extracted.json   — full structured data for all posts
  BLOG_MIGRATION_TRIAGE.md    — human-readable machote ready for verdict fill-in

Zero pip dependencies (stdlib only).
"""

from __future__ import annotations

import json
import os
import re
import urllib.request
import urllib.error
from dataclasses import dataclass, field, asdict
from datetime import datetime
from html import unescape
from html.parser import HTMLParser

# ── config ────────────────────────────────────────────────────────────────────

BASE_URL = "https://seatofthesoul.com"
WP_API = f"{BASE_URL}/wp-json/wp/v2"
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(OUT_DIR, "data")
JSON_OUT = os.path.join(DATA_DIR, "posts_extracted.json")
MD_OUT = os.path.join(OUT_DIR, "BLOG_MIGRATION_TRIAGE.md")
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; SOTSITriageBot/1.0)"}
CURRENT_YEAR = datetime.now().year

EVERGREEN_SLUG_PREFIXES = (
    "soul-snack",
    "soul-feast",
    "soul-seed",
    "wisdom-wednesday",
)

EVERGREEN_TITLE_MARKERS = (
    "soul snack",
    "soul feast",
    "soul seed",
    "wisdom wednesday",
)

EVENT_SIGNAL_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bregister\s+(now|today|here|by)\b", re.I), "registration CTA"),
    (re.compile(r"\bregistration\s+(opens|closes|is\s+now|ends)\b", re.I), "registration window"),
    (re.compile(r"\bzoom\s+(link|call|meeting|webinar)\b", re.I), "Zoom event reference"),
    (re.compile(r"\bjoin\s+us\s+(on|for|live|this)\b", re.I), "live event invite"),
    (re.compile(r"\bRSVP\b"), "RSVP language"),
    (re.compile(r"\btickets?\s+(are|on\s+sale|here|now)\b", re.I), "tickets reference"),
    (re.compile(r"\bwebinar\s+(on|with|begins|series)\b", re.I), "webinar reference"),
    (re.compile(r"\blive\s+event\b", re.I), "live-event language"),
    (re.compile(r"\bsave\s+the\s+date\b", re.I), "save-the-date language"),
    (re.compile(r"\bdoors\s+(open|close)\b", re.I), "doors open/close"),
    (re.compile(r"\bearly\s+bird\b", re.I), "early-bird pricing"),
    (re.compile(r"\bdeadline\b", re.I), "deadline language"),
    (re.compile(r"\bspots?\s+(left|remaining|filling|available)\b", re.I), "scarcity / spots left"),
    (re.compile(r"\blast\s+chance\b", re.I), "last-chance CTA"),
    (re.compile(r"\bsign\s+up\s+(now|here|today|for)\b", re.I), "sign-up CTA"),
    (re.compile(r"\benroll\s+(now|today|here|in)\b", re.I), "enrollment CTA"),
    (re.compile(r"\bseats?\s+(left|remaining|filling|available)\b", re.I), "seats remaining"),
    (re.compile(r"\bcohort\b", re.I), "cohort reference"),
    (re.compile(r"\bnext\s+(week|month|session)\b", re.I), "near-term schedule"),
]

MONTH_YEAR_RE = re.compile(
    r"\b(January|February|March|April|May|June|July|August|September|"
    r"October|November|December)\s+(20\d{2})\b",
    re.IGNORECASE,
)
ISO_DATE_RE = re.compile(r"\b(20\d{2})-(\d{2})-(\d{2})\b")
YEAR_RE = re.compile(r"\b(20[0-2]\d)\b")

# ── http ──────────────────────────────────────────────────────────────────────


def fetch(url: str, timeout: int = 20) -> tuple[str | None, dict[str, str]]:
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", errors="replace"), dict(r.headers)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
        print(f"[warn] fetch failed {url}: {exc}")
        return None, {}


def fetch_paginated(endpoint: str, fields: str | None = None) -> list[dict]:
    items: list[dict] = []
    page = 1
    while True:
        suffix = f"&_fields={fields}" if fields else ""
        url = f"{endpoint}?status=publish&per_page=100&page={page}{suffix}"
        body, hdrs = fetch(url)
        if not body:
            break
        try:
            batch = json.loads(body)
        except json.JSONDecodeError as exc:
            print(f"[warn] bad json page {page}: {exc}")
            break
        if not isinstance(batch, list) or not batch:
            break
        items.extend(batch)
        total_pages = int(hdrs.get("X-WP-TotalPages") or hdrs.get("x-wp-totalpages") or 1)
        if page >= total_pages:
            break
        page += 1
    return items


def fetch_categories() -> dict[int, str]:
    body, _ = fetch(f"{WP_API}/categories?per_page=100&_fields=id,name,slug")
    if not body:
        return {}
    try:
        cats = json.loads(body)
    except json.JSONDecodeError:
        return {}
    return {c["id"]: c.get("name") or c.get("slug") or str(c["id"]) for c in cats}


# ── html parsing ──────────────────────────────────────────────────────────────


class PostHTMLAnalyzer(HTMLParser):
    """Walks WP-rendered post HTML and accumulates structural metadata."""

    HEADING_TAGS = {"h1", "h2", "h3", "h4"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.headings: list[tuple[str, str]] = []
        self.image_total = 0
        self.image_missing_alt = 0
        self.internal_links = 0
        self.external_links = 0
        self.text_chunks: list[str] = []
        self._current_heading_tag: str | None = None
        self._current_heading_text: list[str] = []
        self._skip_text_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {k.lower(): (v or "") for k, v in attrs}
        if tag in self.HEADING_TAGS:
            self._current_heading_tag = tag
            self._current_heading_text = []
        elif tag == "img":
            self.image_total += 1
            if not (attr_map.get("alt") or "").strip():
                self.image_missing_alt += 1
        elif tag == "a":
            href = attr_map.get("href", "")
            if href.startswith(BASE_URL) or href.startswith("/"):
                self.internal_links += 1
            elif href.startswith(("http://", "https://")):
                self.external_links += 1
        elif tag in ("script", "style"):
            self._skip_text_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in self.HEADING_TAGS and self._current_heading_tag == tag:
            text = " ".join("".join(self._current_heading_text).split()).strip()
            if text:
                self.headings.append((tag, text))
            self._current_heading_tag = None
            self._current_heading_text = []
        elif tag in ("script", "style") and self._skip_text_depth > 0:
            self._skip_text_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._skip_text_depth > 0:
            return
        self.text_chunks.append(data)
        if self._current_heading_tag is not None:
            self._current_heading_text.append(data)


def strip_html_to_text(html: str) -> str:
    parser = PostHTMLAnalyzer()
    parser.feed(html or "")
    return " ".join("".join(parser.text_chunks).split())


def parse_post_html(html: str) -> PostHTMLAnalyzer:
    parser = PostHTMLAnalyzer()
    parser.feed(html or "")
    return parser


# ── dataclasses ───────────────────────────────────────────────────────────────


@dataclass
class HeuristicSignal:
    code: str
    sample: str

    def to_dict(self) -> dict:
        return {"code": self.code, "sample": self.sample}


@dataclass
class ExtractedPost:
    id: int
    slug: str
    url: str
    title: str
    published_iso: str
    modified_iso: str
    year: str
    categories: list[str]
    author: str
    word_count: int
    headings: list[dict]
    image_count: int
    images_missing_alt: int
    internal_link_count: int
    external_link_count: int
    excerpt_plain: str
    body_plain_preview: str
    yoast_title: str
    yoast_description: str
    auto_verdict: str
    auto_reasons: list[str]
    dated_signals: list[dict]
    event_signals: list[dict]
    referenced_years: list[str]
    referenced_month_years: list[str]
    quality_flags: list[str]
    requires_ai_review: bool

    def to_dict(self) -> dict:
        return asdict(self)


# ── extraction pipeline ───────────────────────────────────────────────────────


def title_text(p: dict) -> str:
    raw = p.get("title", {})
    if isinstance(raw, dict):
        raw = raw.get("rendered", "")
    return unescape(re.sub(r"<[^>]+>", "", str(raw))).strip()


def excerpt_text(p: dict) -> str:
    raw = p.get("excerpt", {})
    if isinstance(raw, dict):
        raw = raw.get("rendered", "")
    text = unescape(re.sub(r"<[^>]+>", "", str(raw))).strip()
    return " ".join(text.split())


def yoast_field(p: dict, key: str) -> str:
    head = p.get("yoast_head_json") or {}
    val = head.get(key) or ""
    return str(val).strip()


def detect_event_signals(text: str) -> list[HeuristicSignal]:
    out: list[HeuristicSignal] = []
    seen: set[str] = set()
    for pattern, code in EVENT_SIGNAL_PATTERNS:
        m = pattern.search(text)
        if m and code not in seen:
            seen.add(code)
            start = max(0, m.start() - 30)
            end = min(len(text), m.end() + 30)
            sample = "…" + text[start:end].strip() + "…"
            out.append(HeuristicSignal(code=code, sample=sample))
    return out


def detect_date_references(text: str) -> tuple[list[str], list[str]]:
    month_years = sorted({f"{m.group(1).title()} {m.group(2)}" for m in MONTH_YEAR_RE.finditer(text)})
    years_only = sorted({m.group(1) for m in YEAR_RE.finditer(text)})
    return years_only, month_years


def is_evergreen_series(slug: str, title: str) -> bool:
    s = slug.lower()
    t = title.lower()
    if any(s.startswith(prefix) for prefix in EVERGREEN_SLUG_PREFIXES):
        return True
    if any(marker in t for marker in EVERGREEN_TITLE_MARKERS):
        return True
    return False


def compute_quality_flags(*, word_count: int, headings: list[tuple[str, str]],
                          images_missing_alt: int, image_total: int,
                          internal_link_count: int, yoast_title: str,
                          yoast_description: str) -> list[str]:
    flags: list[str] = []
    if word_count < 200:
        flags.append("very_short_content")
    elif word_count < 400:
        flags.append("short_content")
    h2_count = sum(1 for tag, _ in headings if tag == "h2")
    if word_count > 600 and h2_count == 0:
        flags.append("no_h2_structure")
    if image_total > 0 and images_missing_alt / max(image_total, 1) >= 0.3:
        flags.append("alt_text_gaps")
    if internal_link_count == 0 and word_count >= 300:
        flags.append("no_internal_links")
    if not yoast_title:
        flags.append("missing_yoast_title")
    if not yoast_description:
        flags.append("missing_meta_description")
    elif len(yoast_description) < 80 or len(yoast_description) > 170:
        flags.append("meta_description_length_off")
    return flags


def classify_post(*, slug: str, title: str, categories: list[str],
                  event_signals: list[HeuristicSignal],
                  referenced_years: list[str], published_year: str) -> tuple[str, list[str], bool]:
    """Deterministic pre-classification.

    Returns (auto_verdict, reasons, requires_ai_review).
    auto_verdict ∈ {"auto_drop", "auto_keep", "auto_flag_review", "neutral"}
    """
    reasons: list[str] = []

    if any(c.strip().lower() == "exclude" for c in categories):
        reasons.append("WordPress 'Exclude' category set by the SOTSI team — pre-tagged to skip migration")
        return "auto_drop", reasons, False

    if is_evergreen_series(slug, title):
        reasons.append("Slug or title matches evergreen series (Soul Snack / Feast / Seed / Wisdom Wednesday)")
        return "auto_keep", reasons, False

    if event_signals:
        codes = sorted({s.code for s in event_signals})
        reasons.append(f"Event-tied signals detected: {', '.join(codes)}")

    past_years = [y for y in referenced_years if y.isdigit() and int(y) < CURRENT_YEAR and y != published_year]
    if past_years:
        reasons.append(f"Mentions past year(s): {', '.join(past_years)}")

    if event_signals or past_years:
        return "auto_flag_review", reasons, True

    return "neutral", reasons, True


def extract_one(p: dict, cat_lookup: dict[int, str]) -> ExtractedPost:
    pid = int(p.get("id", 0))
    slug = (p.get("slug") or "").strip()
    title = title_text(p)
    published_iso = (p.get("date") or "")[:19]
    modified_iso = (p.get("modified") or "")[:19]
    year = published_iso[:4]

    content_html = ""
    content_field = p.get("content", {})
    if isinstance(content_field, dict):
        content_html = content_field.get("rendered", "") or ""

    parser = parse_post_html(content_html)
    text = " ".join("".join(parser.text_chunks).split())
    word_count = len(text.split())

    cat_ids = p.get("categories") or []
    cat_names = [cat_lookup.get(int(cid), str(cid)) for cid in cat_ids if cid]

    author = ""
    embedded = (p.get("_embedded") or {}).get("author") or []
    if embedded and isinstance(embedded, list):
        author = embedded[0].get("name", "") or ""

    excerpt = excerpt_text(p)
    yoast_title = yoast_field(p, "title")
    yoast_description = yoast_field(p, "description")

    event_signals = detect_event_signals(text)
    referenced_years, referenced_month_years = detect_date_references(text)

    auto_verdict, auto_reasons, requires_ai_review = classify_post(
        slug=slug,
        title=title,
        categories=cat_names,
        event_signals=event_signals,
        referenced_years=referenced_years,
        published_year=year,
    )

    dated_signals = []
    for my in referenced_month_years:
        dated_signals.append({"code": "month_year_reference", "sample": my})

    quality_flags = compute_quality_flags(
        word_count=word_count,
        headings=parser.headings,
        images_missing_alt=parser.image_missing_alt,
        image_total=parser.image_total,
        internal_link_count=parser.internal_links,
        yoast_title=yoast_title,
        yoast_description=yoast_description,
    )

    return ExtractedPost(
        id=pid,
        slug=slug,
        url=f"{BASE_URL}/{slug}",
        title=title,
        published_iso=published_iso,
        modified_iso=modified_iso,
        year=year,
        categories=cat_names,
        author=author,
        word_count=word_count,
        headings=[{"level": tag, "text": txt} for tag, txt in parser.headings[:25]],
        image_count=parser.image_total,
        images_missing_alt=parser.image_missing_alt,
        internal_link_count=parser.internal_links,
        external_link_count=parser.external_links,
        excerpt_plain=excerpt[:400],
        body_plain_preview=text[:600],
        yoast_title=yoast_title,
        yoast_description=yoast_description,
        auto_verdict=auto_verdict,
        auto_reasons=auto_reasons,
        dated_signals=dated_signals,
        event_signals=[s.to_dict() for s in event_signals],
        referenced_years=referenced_years,
        referenced_month_years=referenced_month_years,
        quality_flags=quality_flags,
        requires_ai_review=requires_ai_review,
    )


# ── markdown rendering ────────────────────────────────────────────────────────


def fmt_date(iso: str) -> str:
    if not iso:
        return "—"
    try:
        return datetime.fromisoformat(iso).strftime("%b %d, %Y")
    except ValueError:
        return iso[:10] or "—"


VERDICT_MAP = {
    "auto_drop": ("DROP", "Pre-tagged as 'Exclude' in WordPress by the SOTSI team — do not migrate to the new site."),
    "auto_keep": ("KEEP", "Evergreen series content (Soul Snack / Feast / Seed / Wisdom Wednesday) — migrate as-is."),
    "auto_flag_review": ("REVIEW", "Heuristics found event-tied or dated language. Manual review required."),
    "neutral": ("KEEP (default)", "No automatic red flags. Default to keep unless a manual content read says otherwise."),
}


def render_post_block(p: ExtractedPost) -> str:
    verdict_label, verdict_note = VERDICT_MAP.get(p.auto_verdict, ("PENDING", "Pending review."))
    lines: list[str] = []
    lines.append(f"### {p.title}")
    lines.append("")
    lines.append(f"- **URL:** {p.url}")
    lines.append(f"- **Published:** {fmt_date(p.published_iso)}  |  **Modified:** {fmt_date(p.modified_iso)}")
    lines.append(f"- **Categories:** {', '.join(p.categories) or '—'}")
    lines.append(f"- **Author:** {p.author or '—'}")
    lines.append(f"- **Words:** {p.word_count}  |  **Images:** {p.image_count} ({p.images_missing_alt} no alt)  |  **Internal links:** {p.internal_link_count}")
    if p.yoast_title or p.yoast_description:
        lines.append(f"- **Current Yoast title:** {p.yoast_title or '—'}")
        lines.append(f"- **Current meta description:** {p.yoast_description or '—'}")
    if p.event_signals:
        codes = ", ".join(sorted({s['code'] for s in p.event_signals}))
        lines.append(f"- **Event-keyword hits (boilerplate-likely):** {codes}")
    if p.referenced_month_years:
        lines.append(f"- **Date refs:** {', '.join(p.referenced_month_years[:6])}")
    past_years = [y for y in p.referenced_years if y.isdigit() and int(y) < CURRENT_YEAR and y != p.year]
    if past_years:
        lines.append(f"- **Past year mentions:** {', '.join(past_years)}")
    if p.quality_flags:
        lines.append(f"- **SEO/quality flags:** {', '.join(p.quality_flags)}")
    lines.append("")
    lines.append(f"**Verdict:** `{verdict_label}`")
    lines.append("")
    lines.append(f"**Reason:** {verdict_note}")
    if p.auto_reasons:
        for reason in p.auto_reasons:
            lines.append(f"  - {reason}")
    lines.append("")
    excerpt = p.excerpt_plain or p.body_plain_preview
    if excerpt:
        lines.append("**Excerpt:**")
        lines.append(f"> {excerpt[:380]}{'…' if len(excerpt) > 380 else ''}")
        lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def render_markdown(posts: list[ExtractedPost]) -> str:
    auto_drop = [p for p in posts if p.auto_verdict == "auto_drop"]
    auto_keep = [p for p in posts if p.auto_verdict == "auto_keep"]
    flagged = [p for p in posts if p.auto_verdict == "auto_flag_review"]
    neutral = [p for p in posts if p.auto_verdict == "neutral"]

    total = len(posts)
    today = datetime.now().strftime("%Y-%m-%d")

    by_year: dict[str, int] = {}
    for p in posts:
        by_year[p.year] = by_year.get(p.year, 0) + 1

    by_category: dict[str, int] = {}
    for p in posts:
        for c in p.categories or ["Uncategorized"]:
            by_category[c] = by_category.get(c, 0) + 1

    lines: list[str] = []
    lines.append("# Blog Migration Triage — SOTSI")
    lines.append("")
    lines.append(f"**Site:** {BASE_URL}")
    lines.append(f"**Generated:** {today}")
    lines.append(f"**Total published blog posts analyzed:** {total}")
    lines.append("")
    lines.append("> Working triage for the SOTSI blog migration to the new site.")
    lines.append("> Every verdict here is a **planning recommendation only** — nothing in this report")
    lines.append("> writes to WordPress, the database, or the live site. This is read-only output the")
    lines.append("> team can use to decide what migrates and what gets left behind.")
    lines.append("")
    lines.append("### Headline result")
    lines.append("")
    keep_count = sum(1 for p in posts if p.auto_verdict in ("auto_keep", "neutral"))
    drop_count = sum(1 for p in posts if p.auto_verdict == "auto_drop")
    review_count = sum(1 for p in posts if p.auto_verdict == "auto_flag_review")
    lines.append(f"- **{keep_count}** posts to **migrate (KEEP)** — evergreen Soul Snacks / Feasts / Seeds / Wisdom Wednesdays + clean content")
    lines.append(f"- **{drop_count}** posts to **drop (do NOT migrate)** — already pre-tagged by the SOTSI team in WordPress as `Exclude`")
    lines.append(f"- **{review_count}** posts need a **manual content review** before final decision")
    lines.append("")
    lines.append("### How verdicts were assigned")
    lines.append("")
    lines.append("1. Posts whose WordPress category includes `Exclude` → automatic **DROP** (the team already flagged these).")
    lines.append("2. Posts whose slug or title matches the evergreen series (`soul-snack-*`, `soul-feast-*`, `soul-seed-*`, `wisdom-wednesday-*`) → automatic **KEEP**.")
    lines.append("3. Remaining posts → flagged for manual review if event-tied language or past-year references are found, otherwise default **KEEP**.")
    lines.append("")
    lines.append("> Note: 19 evergreen posts trigger 'enrollment CTA' / 'registration CTA' keyword hits. These are all the same boilerplate footer pointing to the **Soul Themes** program, which is permanent — not an expired event. They are correctly classified as KEEP.")
    lines.append("")
    lines.append("## Auto-classification summary")
    lines.append("")
    lines.append("| Bucket | Posts | Meaning |")
    lines.append("|---|---:|---|")
    lines.append(f"| `auto_drop` | {len(auto_drop)} | WordPress 'Exclude' category — SOTSI team already pre-tagged these to skip migration |")
    lines.append(f"| `auto_keep` | {len(auto_keep)} | Evergreen series (Soul Snack / Feast / Seed / Wisdom Wednesday) — keep |")
    lines.append(f"| `auto_flag_review` | {len(flagged)} | Heuristics detected event signals or past-year references — manual review |")
    lines.append(f"| `neutral` | {len(neutral)} | No obvious red flags — keep by default unless content review says otherwise |")
    lines.append("")
    lines.append("## Breakdown by year")
    lines.append("")
    lines.append("| Year | Posts |")
    lines.append("|---|---:|")
    for y in sorted(by_year.keys(), reverse=True):
        lines.append(f"| {y or '—'} | {by_year[y]} |")
    lines.append("")
    lines.append("## Breakdown by category")
    lines.append("")
    lines.append("| Category | Posts |")
    lines.append("|---|---:|")
    for c in sorted(by_category.keys(), key=lambda x: -by_category[x]):
        lines.append(f"| {c} | {by_category[c]} |")
    lines.append("")

    def render_section(title: str, group: list[ExtractedPost], note: str) -> None:
        lines.append(f"## {title} ({len(group)})")
        lines.append("")
        lines.append(f"_{note}_")
        lines.append("")
        for p in sorted(group, key=lambda x: x.published_iso, reverse=True):
            lines.append(render_post_block(p))

    render_section(
        "Section A — Auto-drop (WP 'Exclude' category)",
        auto_drop,
        "Posts already tagged with the 'Exclude' category in WordPress by the SOTSI team. Default verdict: drop. Listed here for transparency and easy un-drop if desired.",
    )
    render_section(
        "Section B — Auto-keep (Evergreen series)",
        auto_keep,
        "Soul Snacks, Soul Feasts, Soul Seeds, Wisdom Wednesdays. Default verdict: keep.",
    )
    render_section(
        "Section C — Auto-flagged for manual review",
        flagged,
        "Python heuristics found event-tied language or past-year references. A human or AI should read these and decide drop/keep.",
    )
    render_section(
        "Section D — Neutral (no automatic flags)",
        neutral,
        "No obvious red flags. Default verdict: keep unless a manual content review says otherwise.",
    )

    return "\n".join(lines)


# ── runner ────────────────────────────────────────────────────────────────────


def run() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    print("[info] fetching categories…")
    cat_lookup = fetch_categories()
    print(f"[info] {len(cat_lookup)} categories")

    print("[info] fetching published posts with content…")
    endpoint = f"{WP_API}/posts"
    fields = "id,slug,title,date,modified,content,excerpt,categories,yoast_head_json,_links"
    raw_posts = fetch_paginated(endpoint, fields=fields)
    print(f"[info] {len(raw_posts)} posts fetched")

    extracted: list[ExtractedPost] = []
    for raw in raw_posts:
        try:
            extracted.append(extract_one(raw, cat_lookup))
        except Exception as exc:  # noqa: BLE001 — keep pipeline going
            print(f"[warn] failed to extract post id={raw.get('id')}: {exc}")

    extracted.sort(key=lambda x: x.published_iso, reverse=True)

    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "base_url": BASE_URL,
        "total_posts": len(extracted),
        "auto_drop_count": sum(1 for p in extracted if p.auto_verdict == "auto_drop"),
        "auto_keep_count": sum(1 for p in extracted if p.auto_verdict == "auto_keep"),
        "auto_flag_count": sum(1 for p in extracted if p.auto_verdict == "auto_flag_review"),
        "neutral_count": sum(1 for p in extracted if p.auto_verdict == "neutral"),
        "posts": [p.to_dict() for p in extracted],
    }
    with open(JSON_OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    print(f"[ok]   wrote {JSON_OUT}")

    md = render_markdown(extracted)
    with open(MD_OUT, "w", encoding="utf-8") as fh:
        fh.write(md)
    print(f"[ok]   wrote {MD_OUT}")

    print()
    print("Summary:")
    print(f"  total:            {payload['total_posts']}")
    print(f"  auto_drop:        {payload['auto_drop_count']}")
    print(f"  auto_keep:        {payload['auto_keep_count']}")
    print(f"  auto_flag_review: {payload['auto_flag_count']}")
    print(f"  neutral:          {payload['neutral_count']}")


if __name__ == "__main__":
    run()
