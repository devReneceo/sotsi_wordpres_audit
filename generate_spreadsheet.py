"""Generate Christopher's blog migration spreadsheets from data/posts_extracted.json.

Outputs:
  - SOTSI_Blog_Posts_Triage.csv  (all 187 posts, URL first column, sortable in Excel/Sheets)
  - SOTSI_Blog_Posts_Drops.csv   (just the 20 drops, slim view)

Stdlib only. Run after extract_blog_data.py.
"""

from __future__ import annotations

import csv
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "posts_extracted.json"
OUT_ALL = ROOT / "SOTSI_Blog_Posts_Triage.csv"
OUT_DROPS = ROOT / "SOTSI_Blog_Posts_Drops.csv"
OUT_QUICKWINS = ROOT / "SOTSI_Blog_SEO_QuickWins.csv"

SERIES_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("Soul Snack", re.compile(r"\bsoul[-\s]?snack\b", re.IGNORECASE)),
    ("Soul Feast", re.compile(r"\bsoul[-\s]?feast\b", re.IGNORECASE)),
    ("Soul Seed", re.compile(r"\bsoul[-\s]?seed\b", re.IGNORECASE)),
    ("Wisdom Wednesday", re.compile(r"\bwisdom[-\s]?wednesday\b", re.IGNORECASE)),
]

SEO_TITLE_MIN = 30
SEO_TITLE_MAX = 65
SEO_META_MIN = 120
SEO_META_MAX = 160
CONTENT_THIN = 300
CONTENT_SHORT = 500
INTERNAL_LINKS_GOOD = 3


def _score_title(length: int) -> tuple[int, str]:
    if length == 0:
        return 0, "Missing SEO title"
    if length < SEO_TITLE_MIN:
        return 10, f"Title too short ({length} chars, aim {SEO_TITLE_MIN}-{SEO_TITLE_MAX})"
    if length > SEO_TITLE_MAX:
        return 10, f"Title too long ({length} chars, aim {SEO_TITLE_MIN}-{SEO_TITLE_MAX})"
    return 20, ""


def _score_meta(length: int) -> tuple[int, str]:
    if length == 0:
        return 0, f"Add meta description ({SEO_META_MIN}-{SEO_META_MAX} chars)"
    if length < SEO_META_MIN:
        return 10, f"Meta description too short ({length} chars, aim {SEO_META_MIN}-{SEO_META_MAX})"
    if length > SEO_META_MAX:
        return 10, f"Meta description too long ({length} chars, aim {SEO_META_MIN}-{SEO_META_MAX})"
    return 20, ""


def _score_content(words: int) -> tuple[int, str]:
    if words < CONTENT_THIN:
        return 0, f"Thin content ({words} words, expand past {CONTENT_THIN})"
    if words < CONTENT_SHORT:
        return 12, f"Short content ({words} words, ideal {CONTENT_SHORT}+)"
    return 20, ""


def _score_alt(missing: int, total: int) -> tuple[int, str]:
    if total == 0:
        return 20, ""
    if missing == 0:
        return 20, ""
    ratio = 1 - (missing / total)
    points = max(0, int(round(ratio * 20)))
    return points, f"Add alt text to {missing} of {total} images"


def _score_internal_links(count: int) -> tuple[int, str]:
    if count >= INTERNAL_LINKS_GOOD:
        return 20, ""
    if count == 0:
        return 0, f"Add internal links (currently 0, aim {INTERNAL_LINKS_GOOD}+)"
    return 10, f"Add more internal links (currently {count}, aim {INTERNAL_LINKS_GOOD}+)"


def _score_h1(headings: dict | list) -> str:
    # WP theme renders the post title as the page H1 outside content.rendered,
    # so absence of H1 inside the body is expected. Only flag duplicates.
    h1_count = 0
    if isinstance(headings, dict):
        h1_count = len(headings.get("h1", []) or [])
    elif isinstance(headings, list):
        h1_count = sum(1 for h in headings if str(h.get("level", "")).lower() == "h1")
    if h1_count > 1:
        return f"Multiple H1s in body ({h1_count}); keep only one"
    return ""


def compute_seo(post: dict) -> dict:
    yoast_title = clean_text(post.get("yoast_title", ""))
    yoast_desc = clean_text(post.get("yoast_description", ""))
    words = int(post.get("word_count", 0) or 0)
    images = int(post.get("image_count", 0) or 0)
    missing_alt = int(post.get("images_missing_alt", 0) or 0)
    internal = int(post.get("internal_link_count", 0) or 0)

    title_pts, title_note = _score_title(len(yoast_title))
    meta_pts, meta_note = _score_meta(len(yoast_desc))
    content_pts, content_note = _score_content(words)
    alt_pts, alt_note = _score_alt(missing_alt, images)
    link_pts, link_note = _score_internal_links(internal)
    h1_note = _score_h1(post.get("headings") or {})

    score = title_pts + meta_pts + content_pts + alt_pts + link_pts
    actions = [n for n in (meta_note, alt_note, link_note, content_note, title_note, h1_note) if n]

    return {
        "SEO Score": score,
        "SEO Title Length": len(yoast_title),
        "Meta Description Length": len(yoast_desc),
        "SEO Action Items": "; ".join(actions) if actions else "No critical issues",
    }


def detect_series(slug: str, title: str) -> str:
    haystack = f"{slug} {title}"
    for label, pattern in SERIES_PATTERNS:
        if pattern.search(haystack):
            return label
    return "Other"


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    return html.unescape(str(value)).strip()


def primary_category(categories: list[str]) -> str:
    if not categories:
        return ""
    for cat in categories:
        if cat.lower() not in {"blog", "uncategorized", "exclude"}:
            return clean_text(cat)
    return clean_text(categories[0])


def verdict_label(auto_verdict: str) -> str:
    if auto_verdict == "auto_drop":
        return "DROP"
    if auto_verdict == "auto_keep":
        return "KEEP"
    return "REVIEW"


def build_row(post: dict) -> dict:
    categories = [clean_text(c) for c in post.get("categories", []) if c]
    verdict = verdict_label(post.get("auto_verdict", ""))
    seo = compute_seo(post) if verdict == "KEEP" else {
        "SEO Score": "",
        "SEO Title Length": "",
        "Meta Description Length": "",
        "SEO Action Items": "",
    }
    return {
        "URL": post.get("url", ""),
        "Verdict": verdict,
        "Title": clean_text(post.get("title", "")),
        "Series": detect_series(post.get("slug", ""), post.get("title", "")),
        "Primary Category": primary_category(categories),
        "All Categories": "; ".join(categories),
        "Year": post.get("year", ""),
        "Published Date": (post.get("published_iso") or "")[:10],
        "Word Count": post.get("word_count", 0),
        "Image Count": post.get("image_count", 0),
        "Images Missing Alt": post.get("images_missing_alt", 0),
        "Internal Links": post.get("internal_link_count", 0),
        "External Links": post.get("external_link_count", 0),
        "Yoast SEO Title": clean_text(post.get("yoast_title", "")),
        "Yoast SEO Title Length": seo["SEO Title Length"],
        "Yoast Meta Description": clean_text(post.get("yoast_description", "")),
        "Meta Description Length": seo["Meta Description Length"],
        "SEO Score (0-100)": seo["SEO Score"],
        "SEO Action Items": seo["SEO Action Items"],
        "Reason / Notes": " | ".join(post.get("auto_reasons", [])),
    }


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> None:
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    posts = payload.get("posts", [])

    all_rows = [build_row(p) for p in posts]
    all_rows.sort(
        key=lambda r: (
            0 if r["Verdict"] == "DROP" else 1,
            -(int(r["Year"]) if str(r["Year"]).isdigit() else 0),
            r["Title"].lower(),
        )
    )

    drops_rows = [r for r in all_rows if r["Verdict"] == "DROP"]
    drops_fieldnames = [
        "URL",
        "Title",
        "Year",
        "Primary Category",
        "Reason / Notes",
        "Word Count",
        "Published Date",
    ]
    drops_slim = [{k: r[k] for k in drops_fieldnames} for r in drops_rows]

    keep_rows = [r for r in all_rows if r["Verdict"] == "KEEP"]
    quickwins_fieldnames = [
        "URL",
        "Title",
        "Series",
        "SEO Score (0-100)",
        "Top Action #1",
        "Top Action #2",
        "Top Action #3",
        "Yoast SEO Title Length",
        "Meta Description Length",
        "Word Count",
        "Internal Links",
        "Images Missing Alt",
    ]
    quickwins_rows = []
    for r in sorted(
        keep_rows, key=lambda x: (int(x["SEO Score (0-100)"]), x["Title"].lower())
    ):
        actions = [a.strip() for a in r["SEO Action Items"].split(";") if a.strip()]
        quickwins_rows.append(
            {
                "URL": r["URL"],
                "Title": r["Title"],
                "Series": r["Series"],
                "SEO Score (0-100)": r["SEO Score (0-100)"],
                "Top Action #1": actions[0] if len(actions) > 0 else "",
                "Top Action #2": actions[1] if len(actions) > 1 else "",
                "Top Action #3": actions[2] if len(actions) > 2 else "",
                "Yoast SEO Title Length": r["Yoast SEO Title Length"],
                "Meta Description Length": r["Meta Description Length"],
                "Word Count": r["Word Count"],
                "Internal Links": r["Internal Links"],
                "Images Missing Alt": r["Images Missing Alt"],
            }
        )

    fieldnames = list(all_rows[0].keys())
    write_csv(OUT_ALL, all_rows, fieldnames)
    write_csv(OUT_DROPS, drops_slim, drops_fieldnames)
    write_csv(OUT_QUICKWINS, quickwins_rows, quickwins_fieldnames)

    print(f"Wrote {OUT_ALL.name} ({len(all_rows)} rows)")
    print(f"Wrote {OUT_DROPS.name} ({len(drops_slim)} rows)")
    print(f"Wrote {OUT_QUICKWINS.name} ({len(quickwins_rows)} rows, worst-first)")
    print()
    print("Breakdown:")
    drops = sum(1 for r in all_rows if r["Verdict"] == "DROP")
    keeps = sum(1 for r in all_rows if r["Verdict"] == "KEEP")
    print(f"  DROP: {drops}")
    print(f"  KEEP: {keeps}")
    series_counts: dict[str, int] = {}
    for r in all_rows:
        if r["Verdict"] == "KEEP":
            series_counts[r["Series"]] = series_counts.get(r["Series"], 0) + 1
    print("  KEEP by series:")
    for label, count in sorted(series_counts.items(), key=lambda kv: -kv[1]):
        print(f"    {label}: {count}")


if __name__ == "__main__":
    main()
