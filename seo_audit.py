#!/usr/bin/env python3
"""
SOTSI on-page SEO + tracking audit — v1.

Complements ``audit_sotsi.py`` (which inventories drafts/sitemap/categories).
This script crawls the live WordPress site, extracts on-page SEO signals
(title, meta, schemas, canonical, OG, link counts, imgs without alt…) and
detects which tracking pixels are installed (GA4, UA, GTM, FB Pixel, Hotjar,
Google Search Console verification).

Stdlib only — no pip install required.
Respects ``robots.txt`` ``Crawl-delay: 3`` so the full crawl is a polite ~15 min.
Saves partial progress every 20 URLs so a kill mid-run loses at most 20.

Usage:
    python3 seo_audit.py                  # full crawl (post + page + chapters)
    python3 seo_audit.py --limit 20       # quick sample run
    python3 seo_audit.py --sitemap post   # only the post-sitemap
"""
import argparse
import csv
import gzip
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html.parser import HTMLParser

# ──────────────────────────────────────────────────────────────────────────────
# Config
# ──────────────────────────────────────────────────────────────────────────────
BASE = "https://seatofthesoul.com"
SITEMAP_INDEX = f"{BASE}/sitemap_index.xml"
# Sitemap shortnames → URL; we audit the SEO-relevant ones by default.
SITEMAPS = {
    "post":     f"{BASE}/post-sitemap.xml",
    "page":     f"{BASE}/page-sitemap.xml",
    "chapters": f"{BASE}/chapters-sitemap.xml",
}
USER_AGENT = "Mozilla/5.0 (compatible; SOTSI-SEO-Audit/1.0; 22D Marketing)"
CRAWL_DELAY = 3        # seconds; from robots.txt
TIMEOUT = 25           # per-request timeout
RETRIES = 2            # on 5xx / network errors
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(OUT_DIR, "data")
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")
JSON_OUT = os.path.join(DATA_DIR, f"seo_audit_{TODAY}.json")
CSV_OUT = os.path.join(DATA_DIR, f"seo_audit_{TODAY}.csv")
PROGRESS_OUT = os.path.join(DATA_DIR, f"seo_audit_{TODAY}.progress.json")

# Tracking detection regexes. Each accepts the HTML and yields the matched ID(s).
RE_GA4       = re.compile(r"\bG-[A-Z0-9]{8,12}\b")
RE_UA        = re.compile(r"\bUA-\d{4,10}-\d{1,3}\b")
RE_GTM       = re.compile(r"\bGTM-[A-Z0-9]{4,10}\b")
RE_FB_PIXEL  = re.compile(r"fbq\(\s*['\"]init['\"]\s*,\s*['\"](\d{10,20})['\"]\s*\)")
RE_HOTJAR    = re.compile(r"hjid\s*[:=]\s*(\d{4,10})")
RE_GSC       = re.compile(
    r'<meta\s+name=[\'"]google-site-verification[\'"]\s+content=[\'"]([^\'"]+)[\'"]',
    re.IGNORECASE,
)

# CSV columns — same order as the dict keys for legibility.
CSV_FIELDS = [
    "url", "sitemap", "status", "final_url", "elapsed_ms", "page_kb",
    "title", "title_len", "meta_description", "meta_description_len",
    "h1", "h1_count", "h2_count",
    "canonical", "lang", "robots_meta",
    "og_title", "og_description", "og_image",
    "twitter_card",
    "jsonld_types",
    "word_count_approx", "imgs_total", "imgs_no_alt",
    "internal_links", "external_links",
    "ga4_ids", "ua_ids", "gtm_ids", "fb_pixel_ids", "hotjar_ids", "gsc_verification",
    "audit_severity", "audit_notes",
]


# ──────────────────────────────────────────────────────────────────────────────
# HTTP
# ──────────────────────────────────────────────────────────────────────────────
def fetch(url: str) -> dict:
    """GET ``url`` with retries + gzip handling. Returns a dict with
    ``status``, ``body`` (str), ``final_url``, ``elapsed_ms``, ``size_bytes``."""
    last_err = None
    for attempt in range(RETRIES + 1):
        req = urllib.request.Request(url, headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xml;q=0.9",
            "Accept-Encoding": "gzip",
        })
        start = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                raw = r.read()
                if r.headers.get("Content-Encoding", "").lower() == "gzip":
                    raw = gzip.decompress(raw)
                elapsed_ms = int((time.monotonic() - start) * 1000)
                # Be lax on decoding — fall back to latin-1 if utf-8 fails.
                try:
                    body = raw.decode("utf-8", errors="replace")
                except Exception:
                    body = raw.decode("latin-1", errors="replace")
                return {
                    "status": r.status,
                    "body": body,
                    "final_url": r.geturl(),
                    "elapsed_ms": elapsed_ms,
                    "size_bytes": len(raw),
                }
        except urllib.error.HTTPError as e:
            elapsed_ms = int((time.monotonic() - start) * 1000)
            return {
                "status": e.code,
                "body": "",
                "final_url": url,
                "elapsed_ms": elapsed_ms,
                "size_bytes": 0,
            }
        except Exception as e:
            last_err = e
            time.sleep(1.5 * (attempt + 1))  # back-off then retry
    return {"status": 0, "body": "", "final_url": url, "elapsed_ms": 0, "size_bytes": 0, "error": str(last_err)}


# ──────────────────────────────────────────────────────────────────────────────
# HTML parsing (stdlib only) — tracks tags we care about as a flat stream.
# ──────────────────────────────────────────────────────────────────────────────
class SEOParser(HTMLParser):
    """Stream-parse HTML and accumulate SEO-relevant signals."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.in_title = False
        self.meta_description = ""
        self.canonical = ""
        self.lang = ""
        self.robots_meta = ""
        self.og = {"title": "", "description": "", "image": ""}
        self.twitter_card = ""
        self.jsonld_types: list[str] = []
        self.in_jsonld = False
        self.jsonld_buf: list[str] = []
        self.h1: list[str] = []
        self.in_h1 = False
        self.h1_buf: list[str] = []
        self.h2_count = 0
        self.imgs_total = 0
        self.imgs_no_alt = 0
        self.internal_links = 0
        self.external_links = 0
        # Word counting — approximate, from visible text.
        self.text_buf: list[str] = []
        self.skip_text_depth = 0  # inside script/style/noscript

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang", "") or self.lang
        elif tag == "title":
            self.in_title = True
        elif tag == "meta":
            name = (a.get("name") or "").lower()
            prop = (a.get("property") or "").lower()
            content = a.get("content", "") or ""
            if name == "description":
                self.meta_description = content
            elif name == "robots":
                self.robots_meta = content
            elif name == "twitter:card":
                self.twitter_card = content
            elif prop == "og:title":
                self.og["title"] = content
            elif prop == "og:description":
                self.og["description"] = content
            elif prop == "og:image":
                self.og["image"] = content
        elif tag == "link":
            if (a.get("rel") or "").lower() == "canonical":
                self.canonical = a.get("href", "") or ""
        elif tag == "script":
            if (a.get("type") or "").lower() == "application/ld+json":
                self.in_jsonld = True
                self.jsonld_buf = []
            self.skip_text_depth += 1
        elif tag in ("style", "noscript"):
            self.skip_text_depth += 1
        elif tag == "h1":
            self.in_h1 = True
            self.h1_buf = []
        elif tag == "h2":
            self.h2_count += 1
        elif tag == "img":
            self.imgs_total += 1
            alt = a.get("alt")
            if alt is None or alt.strip() == "":
                self.imgs_no_alt += 1
        elif tag == "a":
            href = (a.get("href") or "").strip()
            if href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:") or not href:
                return
            if href.startswith("http://") or href.startswith("https://"):
                if "seatofthesoul.com" in href:
                    self.internal_links += 1
                else:
                    self.external_links += 1
            else:
                # relative — treat as internal
                self.internal_links += 1

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        elif tag == "script":
            if self.in_jsonld:
                blob = "".join(self.jsonld_buf).strip()
                self.in_jsonld = False
                self.jsonld_buf = []
                # Try to extract @type values — accept arrays + single objects.
                try:
                    data = json.loads(blob)
                    self._collect_jsonld_types(data)
                except Exception:
                    pass
            self.skip_text_depth = max(0, self.skip_text_depth - 1)
        elif tag in ("style", "noscript"):
            self.skip_text_depth = max(0, self.skip_text_depth - 1)
        elif tag == "h1":
            self.in_h1 = False
            text = " ".join("".join(self.h1_buf).split()).strip()
            if text:
                self.h1.append(text)

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        if self.in_jsonld:
            self.jsonld_buf.append(data)
        if self.in_h1:
            self.h1_buf.append(data)
        if self.skip_text_depth == 0:
            self.text_buf.append(data)

    def _collect_jsonld_types(self, node):
        """JSON-LD ``@type`` can be string, list, or nested via ``@graph``."""
        if isinstance(node, dict):
            t = node.get("@type")
            if isinstance(t, str):
                self.jsonld_types.append(t)
            elif isinstance(t, list):
                self.jsonld_types.extend(s for s in t if isinstance(s, str))
            graph = node.get("@graph")
            if isinstance(graph, list):
                for n in graph:
                    self._collect_jsonld_types(n)
        elif isinstance(node, list):
            for n in node:
                self._collect_jsonld_types(n)

    @property
    def word_count_approx(self) -> int:
        text = " ".join(self.text_buf)
        return len([w for w in re.findall(r"\b[\w'-]+\b", text)])


# ──────────────────────────────────────────────────────────────────────────────
# Sitemap discovery
# ──────────────────────────────────────────────────────────────────────────────
def parse_sitemap_urls(xml_text: str) -> list[str]:
    """Return only the page ``<loc>`` URLs from a sitemap (urlset or sitemapindex).

    WordPress sitemaps embed ``<image:image><image:loc>`` for every inline image —
    naively grabbing all ``<loc>`` pulls in image URLs we don't want to audit.
    Solution: only walk direct ``<loc>`` children of ``<url>`` / ``<sitemap>``."""
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []
    locs: list[str] = []
    for parent in root:
        tag = parent.tag.split("}")[-1] if "}" in parent.tag else parent.tag
        if tag not in ("url", "sitemap"):
            continue
        for child in parent:
            ctag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
            if ctag == "loc" and child.text:
                locs.append(child.text.strip())
                break  # only the first <loc> per <url>; skip nested image:loc
    return locs


# ──────────────────────────────────────────────────────────────────────────────
# Audit a single URL
# ──────────────────────────────────────────────────────────────────────────────
def severity_from_signals(rec: dict) -> tuple[str, list[str]]:
    """Bucket findings as CRITICAL / HIGH / MEDIUM / LOW + a list of human notes
    used for Task creation later. Cheap heuristic — refine after sampling."""
    notes: list[str] = []
    severity = "LOW"

    if rec["status"] >= 500 or rec["status"] == 0:
        return "CRITICAL", [f"server error or unreachable (status {rec['status']})"]
    if rec["status"] >= 400:
        return "CRITICAL", [f"client error (status {rec['status']})"]

    if rec["robots_meta"] and "noindex" in rec["robots_meta"].lower():
        severity = "HIGH"
        notes.append(f"noindex meta — won't rank ({rec['robots_meta']})")

    if not rec["title"]:
        severity = "HIGH" if severity == "LOW" else severity
        notes.append("missing <title>")
    elif rec["title_len"] < 25 or rec["title_len"] > 65:
        severity = "MEDIUM" if severity == "LOW" else severity
        notes.append(f"title length {rec['title_len']} (target 25–65)")

    if not rec["meta_description"]:
        severity = "MEDIUM" if severity == "LOW" else severity
        notes.append("missing meta description")
    elif rec["meta_description_len"] < 70 or rec["meta_description_len"] > 165:
        notes.append(f"meta desc length {rec['meta_description_len']} (target 70–165)")

    if rec["h1_count"] == 0:
        severity = "HIGH" if severity == "LOW" else severity
        notes.append("missing H1")
    elif rec["h1_count"] > 1:
        severity = "MEDIUM" if severity == "LOW" else severity
        notes.append(f"multiple H1s ({rec['h1_count']})")

    if not rec["canonical"]:
        severity = "MEDIUM" if severity == "LOW" else severity
        notes.append("missing canonical")

    if not rec["jsonld_types"]:
        notes.append("no JSON-LD schema")

    if rec["imgs_no_alt"] > 0:
        if rec["imgs_no_alt"] >= 5:
            severity = "MEDIUM" if severity == "LOW" else severity
        notes.append(f"{rec['imgs_no_alt']}/{rec['imgs_total']} imgs missing alt")

    if rec["word_count_approx"] < 200:
        severity = "MEDIUM" if severity == "LOW" else severity
        notes.append(f"thin content ({rec['word_count_approx']} words)")

    if rec["page_kb"] > 3000:
        notes.append(f"heavy page ({rec['page_kb']} KB)")

    return severity, notes


def audit_url(url: str, sitemap_key: str) -> dict:
    """Fetch one URL + extract all signals into a flat record."""
    res = fetch(url)
    body = res["body"]
    rec: dict = {
        "url": url,
        "sitemap": sitemap_key,
        "status": res["status"],
        "final_url": res["final_url"],
        "elapsed_ms": res["elapsed_ms"],
        "page_kb": round(res["size_bytes"] / 1024, 1),
        "title": "",
        "title_len": 0,
        "meta_description": "",
        "meta_description_len": 0,
        "h1": "",
        "h1_count": 0,
        "h2_count": 0,
        "canonical": "",
        "lang": "",
        "robots_meta": "",
        "og_title": "",
        "og_description": "",
        "og_image": "",
        "twitter_card": "",
        "jsonld_types": "",
        "word_count_approx": 0,
        "imgs_total": 0,
        "imgs_no_alt": 0,
        "internal_links": 0,
        "external_links": 0,
        "ga4_ids": "",
        "ua_ids": "",
        "gtm_ids": "",
        "fb_pixel_ids": "",
        "hotjar_ids": "",
        "gsc_verification": "",
        "audit_severity": "LOW",
        "audit_notes": "",
    }

    if res["status"] != 200 or not body:
        sev, notes = severity_from_signals(rec)
        rec["audit_severity"] = sev
        rec["audit_notes"] = "; ".join(notes)
        return rec

    # On-page signals
    parser = SEOParser()
    try:
        parser.feed(body)
    except Exception as e:
        rec["audit_notes"] = f"parse error: {e}"
    title = parser.title.strip()
    rec["title"] = title
    rec["title_len"] = len(title)
    rec["meta_description"] = parser.meta_description.strip()
    rec["meta_description_len"] = len(parser.meta_description.strip())
    rec["h1"] = parser.h1[0] if parser.h1 else ""
    rec["h1_count"] = len(parser.h1)
    rec["h2_count"] = parser.h2_count
    rec["canonical"] = parser.canonical
    rec["lang"] = parser.lang
    rec["robots_meta"] = parser.robots_meta
    rec["og_title"] = parser.og["title"]
    rec["og_description"] = parser.og["description"]
    rec["og_image"] = parser.og["image"]
    rec["twitter_card"] = parser.twitter_card
    rec["jsonld_types"] = "|".join(sorted(set(parser.jsonld_types)))
    rec["word_count_approx"] = parser.word_count_approx
    rec["imgs_total"] = parser.imgs_total
    rec["imgs_no_alt"] = parser.imgs_no_alt
    rec["internal_links"] = parser.internal_links
    rec["external_links"] = parser.external_links

    # Tracking — scan the raw HTML for IDs
    def uniq(matches):
        return "|".join(sorted(set(matches))) if matches else ""

    rec["ga4_ids"]   = uniq(RE_GA4.findall(body))
    rec["ua_ids"]    = uniq(RE_UA.findall(body))
    rec["gtm_ids"]   = uniq(RE_GTM.findall(body))
    rec["fb_pixel_ids"] = uniq(RE_FB_PIXEL.findall(body))
    rec["hotjar_ids"]   = uniq(RE_HOTJAR.findall(body))
    gsc = RE_GSC.search(body)
    rec["gsc_verification"] = gsc.group(1) if gsc else ""

    sev, notes = severity_from_signals(rec)
    rec["audit_severity"] = sev
    rec["audit_notes"] = "; ".join(notes)
    return rec


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────
def save_progress(records: list[dict], elapsed_total: float, total_planned: int):
    """Write JSON + CSV + a small progress file. Atomic via tmp + rename."""
    os.makedirs(DATA_DIR, exist_ok=True)
    # JSON full
    tmp = JSON_OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({
            "audited_at": datetime.now(timezone.utc).isoformat(),
            "site": BASE,
            "total_planned": total_planned,
            "total_audited": len(records),
            "elapsed_seconds": round(elapsed_total, 1),
            "records": records,
        }, f, indent=2, ensure_ascii=False)
    os.replace(tmp, JSON_OUT)
    # CSV flattened
    tmp = CSV_OUT + ".tmp"
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(records)
    os.replace(tmp, CSV_OUT)
    # Tiny progress file (cheap to poll)
    with open(PROGRESS_OUT, "w", encoding="utf-8") as f:
        json.dump({
            "audited": len(records),
            "planned": total_planned,
            "pct": round(len(records) / total_planned * 100, 1) if total_planned else 0,
            "elapsed_s": round(elapsed_total, 1),
        }, f)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sitemap", choices=list(SITEMAPS.keys()) + ["all"], default="all",
                    help="Which sitemap to crawl (default: all SEO-relevant)")
    ap.add_argument("--limit", type=int, default=0, help="Max URLs total (0 = no limit)")
    ap.add_argument("--delay", type=float, default=CRAWL_DELAY,
                    help=f"Crawl delay seconds (default {CRAWL_DELAY}, from robots.txt)")
    args = ap.parse_args()

    sitemaps = SITEMAPS if args.sitemap == "all" else {args.sitemap: SITEMAPS[args.sitemap]}

    # Discover URL list per sitemap.
    all_urls: list[tuple[str, str]] = []  # (url, sitemap_key)
    for key, sm_url in sitemaps.items():
        print(f"[discover] {key}: {sm_url}", flush=True)
        r = fetch(sm_url)
        if r["status"] != 200:
            print(f"  ⚠ sitemap fetch failed status={r['status']}", flush=True)
            continue
        urls = parse_sitemap_urls(r["body"])
        print(f"  → {len(urls)} URLs", flush=True)
        for u in urls:
            all_urls.append((u, key))
        time.sleep(args.delay)

    if args.limit > 0:
        all_urls = all_urls[: args.limit]
    total = len(all_urls)
    print(f"\n[crawl] {total} URLs, delay={args.delay}s, ETA ≈ {round(total * (args.delay + 1) / 60, 1)} min\n", flush=True)

    records: list[dict] = []
    start = time.monotonic()
    for i, (url, key) in enumerate(all_urls, start=1):
        rec = audit_url(url, key)
        records.append(rec)
        # Compact progress line every URL
        sev = rec["audit_severity"]
        marker = {"CRITICAL": "✗", "HIGH": "!", "MEDIUM": "·", "LOW": "✓"}.get(sev, "?")
        print(f"  [{i:>3}/{total}] {marker} {sev:<8} {url}", flush=True)
        # Save partial every 20 URLs so kills lose at most 20.
        if i % 20 == 0:
            save_progress(records, time.monotonic() - start, total)
            print(f"    💾 partial saved → {len(records)} records", flush=True)
        # Polite delay between requests.
        if i < total:
            time.sleep(args.delay)

    save_progress(records, time.monotonic() - start, total)
    print(f"\n[done] {len(records)} URLs audited in {round((time.monotonic()-start)/60, 1)} min", flush=True)
    print(f"  JSON: {JSON_OUT}", flush=True)
    print(f"  CSV : {CSV_OUT}", flush=True)
    print(_summary(records), flush=True)


def _summary(records: list[dict]) -> str:
    """Tiny one-screen rollup printed at the end."""
    by_sev: dict[str, int] = {}
    track_ga4 = track_ua = track_gtm = track_fb = track_hj = 0
    no_canonical = no_h1 = no_meta_desc = noindex = thin = 0
    for r in records:
        by_sev[r["audit_severity"]] = by_sev.get(r["audit_severity"], 0) + 1
        if r["ga4_ids"]: track_ga4 += 1
        if r["ua_ids"]: track_ua += 1
        if r["gtm_ids"]: track_gtm += 1
        if r["fb_pixel_ids"]: track_fb += 1
        if r["hotjar_ids"]: track_hj += 1
        if not r["canonical"]: no_canonical += 1
        if r["h1_count"] == 0: no_h1 += 1
        if not r["meta_description"]: no_meta_desc += 1
        if r["robots_meta"] and "noindex" in r["robots_meta"].lower(): noindex += 1
        if 0 < r["word_count_approx"] < 200: thin += 1
    lines = [
        "\n──── ROLLUP ────",
        f"Severity: " + " ".join(f"{k}={v}" for k, v in by_sev.items()),
        f"Tracking present: GA4={track_ga4}  UA={track_ua}  GTM={track_gtm}  FB={track_fb}  Hotjar={track_hj}",
        f"On-page gaps: no_canonical={no_canonical}  no_h1={no_h1}  no_meta_desc={no_meta_desc}  noindex={noindex}  thin={thin}",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
