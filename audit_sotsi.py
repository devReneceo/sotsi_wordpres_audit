"""
SOTSI WordPress Site Audit — v5
Brand: Luno dashboard (navy #1c2333, primary #405189, Nunito font).
Features: scroll tables, iframe loader, draft pages tab, clickable sitemap tiles.
"""

import urllib.request
import json
import re
import os
from datetime import datetime

BASE_URL = "https://seatofthesoul.com"
WP_API   = f"{BASE_URL}/wp-json/wp/v2"
OUT_DIR  = os.path.dirname(os.path.abspath(__file__))
HTML_OUT = os.path.join(OUT_DIR, "SOTSI_Audit_Report.html")
HEADERS  = {"User-Agent": "Mozilla/5.0 (compatible; SiteAuditBot/1.0)"}

# ── draft pages (from WP Admin — not accessible via public API) ───────────────

DRAFT_PAGES = [
    {"title":"Journey to the Soul 2023 Year Long Program","author":"Timothy Farzalo","last_modified":"2022-07-13 21:51","status":"draft"},
    {"title":"Journey to the Soul Registration (2022 – Intention is Everything)","author":"SOTS","last_modified":"2021-12-03 14:30","status":"draft"},
    {"title":"Journey to the Soul Retreat 2021","author":"SOTS","last_modified":"2021-07-27 05:32","status":"draft"},
    {"title":"Journey to the Soul Retreat","author":"SOTS","last_modified":"2021-09-24 06:28","status":"draft"},
    {"title":"Journey to the Soul Registration (October Event)","author":"Timothy Farzalo","last_modified":"2022-06-04 02:55","status":"draft"},
    {"title":"Journey to the Soul Multisensory Life","author":"SOTS","last_modified":"2021-11-30 21:19","status":"draft"},
    {"title":"Journey to the Soul Intention Is Everything","author":"SOTS","last_modified":"2022-04-18 13:59","status":"draft"},
    {"title":"Journey to the Soul Cultivating Emotional Awareness","author":"SOTS","last_modified":"2022-01-11 19:35","status":"draft"},
    {"title":"SPP 23 Registration","author":"Timothy Farzalo","last_modified":"2022-11-11 19:46","status":"draft"},
    {"title":"Spiritual Partnership Program (SPP) Registration 2024","author":"Timothy Farzalo","last_modified":"2023-10-13 20:16","status":"draft"},
    {"title":"Spiritual Partnership Program (SPP) Registration 2023","author":"Timothy Farzalo","last_modified":"2022-11-11 20:24","status":"draft"},
    {"title":"Spiritual Partnership Event","author":"SOTS","last_modified":"2021-10-29 05:34","status":"draft"},
    {"title":"Authentic Power Support Program (APSP) 2023","author":"Timothy Farzalo","last_modified":"2022-11-11 20:24","status":"draft"},
    {"title":"Authentic Power Guidelines Course: Special Series | Ground Rules","author":"Timothy Farzalo","last_modified":"2023-08-24 19:33","status":"draft"},
    {"title":"Membership Cancel","author":"Timothy Farzalo","last_modified":"2023-01-30 06:24","status":"draft"},
    {"title":"Membership Checkout","author":"Timothy Farzalo","last_modified":"2023-01-30 06:24","status":"draft"},
    {"title":"Membership Confirmation","author":"Timothy Farzalo","last_modified":"2023-01-30 06:24","status":"draft"},
    {"title":"Membership Account","author":"Timothy Farzalo","last_modified":"2023-01-30 06:24","status":"draft"},
    {"title":"Membership Billing","author":"Timothy Farzalo","last_modified":"2023-01-30 06:24","status":"draft"},
    {"title":"Membership Invoice","author":"Timothy Farzalo","last_modified":"2023-01-30 06:24","status":"draft"},
    {"title":"Membership Levels","author":"Timothy Farzalo","last_modified":"2023-01-30 06:24","status":"draft"},
    {"title":"Log In","author":"Timothy Farzalo","last_modified":"2023-01-30 06:24","status":"draft"},
    {"title":"Plan Confirmation","author":"Timothy Farzalo","last_modified":"2023-01-30 06:58","status":"draft"},
    {"title":"Journey to the Soul Retreat","author":"Timothy Farzalo","last_modified":"2021-11-11 07:20","status":"draft"},
    {"title":"Special Registration","author":"Timothy Farzalo","last_modified":"2022-04-02 00:45","status":"draft"},
    {"title":"Retreat FAQs","author":"SOTS","last_modified":"2021-12-07 00:09","status":"draft"},
    {"title":"Elementor #13138","author":"SOTS","last_modified":"2021-11-02 07:28","status":"draft"},
    {"title":"Refund and Returns Policy","author":"SOTS","last_modified":"2021-11-01 20:26","status":"draft"},
    {"title":"Events","author":"SOTS","last_modified":"2021-10-30 15:32","status":"draft"},
    {"title":"STUDY GUIDE EXTENSION","author":"SOTS","last_modified":"2021-06-28 10:12","status":"draft"},
    {"title":"Journey to the Soul Retreat 2021","author":"SOTS","last_modified":"2021-08-10 07:42","status":"draft"},
    {"title":"STUDY GUIDE EXTENSION Backup","author":"SOTS","last_modified":"2021-07-29 09:26","status":"draft"},
    {"title":"Retreat FAQ's","author":"SOTS","last_modified":"2021-07-08 05:57","status":"draft"},
    {"title":"Welcome","author":"SOTS","last_modified":"2021-07-05 05:14","status":"draft"},
    {"title":"Life School","author":"SOTS","last_modified":"2021-04-06 05:10","status":"draft"},
]

# ── draft posts (from WP Admin — not accessible via public API) ───────────────

DRAFT_POSTS = [
    {"title":"Soul Snack #25 – What is Evil?","author":"SOTS","categories":"Uncategorized","last_modified":"2025-03-12 14:02","status":"draft"},
    {"title":"The Compassion Virus","author":"SOTS","categories":"Blog, Exclude","last_modified":"2021-03-10 21:05","status":"draft"},
    {"title":"MULTISENSORY THANKS GIVING","author":"Gary Zukav","categories":"Blog, Exclude","last_modified":"2021-03-20 07:56","status":"draft"},
    {"title":"KAVANAUGH HEARING AND SPIRITUAL GROWTH","author":"Gary Zukav","categories":"Blog, Exclude","last_modified":"2021-03-20 08:40","status":"draft"},
    {"title":"WHAT TO DO WHEN YOU HAVE A BROKEN HEART","author":"Gary Zukav","categories":"Blog, Exclude","last_modified":"2021-03-20 08:42","status":"draft"},
    {"title":"The Most Dangerous Virus","author":"Gary Zukav","categories":"Blog, Exclude","last_modified":"2021-03-20 08:43","status":"draft"},
    {"title":"WHAT ILLUSIONS ARE YOU CAUGHT IN?","author":"Gary Zukav","categories":"Blog, Exclude","last_modified":"2021-03-23 11:41","status":"draft"},
    {"title":"Love, Fear, and the Coronavirus","author":"Gary Zukav","categories":"Blog, Exclude","last_modified":"2021-03-20 07:55","status":"draft"},
    {"title":"SYMPHONY OF PEACE PRAYERS","author":"Gary Zukav","categories":"Blog, Exclude","last_modified":"2021-04-19 07:57","status":"draft"},
    {"title":"SMALL THINGS WITH GREAT LOVE","author":"Gary Zukav","categories":"Blog, Exclude","last_modified":"2021-04-19 08:04","status":"draft"},
    {"title":"A DIFFERENT EXPERIENCE OF CHRISTMAS","author":"Gary Zukav","categories":"Blog, Exclude","last_modified":"2021-04-19 08:10","status":"draft"},
    {"title":"SPIRITUAL GROWTH AND SEXUAL ABUSE","author":"Gary Zukav","categories":"Blog, Exclude","last_modified":"2021-04-19 08:16","status":"draft"},
    {"title":"SPIRITUAL PARTNERSHIPS AND FRIENDSHIPS","author":"Gary Zukav","categories":"Blog, Exclude","last_modified":"2021-04-19 07:47","status":"draft"},
    {"title":"THANKS AND GIVING","author":"Gary Zukav","categories":"Blog, Exclude","last_modified":"2021-04-19 08:25","status":"draft"},
    {"title":"YOUR BUCKET LIST","author":"Gary Zukav","categories":"Blog, Exclude","last_modified":"2021-04-19 08:30","status":"draft"},
    {"title":"LAS VEGAS – CLOSE TO HOME","author":"Gary Zukav","categories":"Blog, Exclude","last_modified":"2021-04-19 08:35","status":"draft"},
    {"title":"TOTAL ECLIPSE","author":"Gary Zukav","categories":"Blog, Exclude","last_modified":"2021-04-20 06:03","status":"draft"},
]

# ── network ───────────────────────────────────────────────────────────────────

def fetch(url, timeout=15):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", errors="replace"), r.headers
    except Exception:
        return None, None

def fetch_all_paginated(endpoint):
    items, page = [], 1
    while True:
        url = (f"{endpoint}?per_page=100&page={page}"
               f"&_fields=id,slug,title,status,date,modified")
        body, hdrs = fetch(url)
        if not body:
            break
        batch = json.loads(body)
        if not batch:
            break
        items.extend(batch)
        total_pages = int((hdrs.get("X-WP-TotalPages") or hdrs.get("x-wp-totalpages") or 1))
        if page >= total_pages:
            break
        page += 1
    return items

# ── helpers ───────────────────────────────────────────────────────────────────

def fmt_date(iso):
    try:
        return datetime.fromisoformat(iso).strftime("%b %d, %Y")
    except Exception:
        return iso or "—"

def title_text(p):
    t = p.get("title", {})
    raw = t.get("rendered", "") if isinstance(t, dict) else str(t)
    raw = re.sub(r"<[^>]+>", "", raw)
    for ent, ch in [("&#8211;","–"),("&#038;","&"),("&#8217;","'"),
                    ("&#8220;",'"'),("&#8221;",'"'),("&amp;","&")]:
        raw = raw.replace(ent, ch)
    return raw

# ── sitemap ───────────────────────────────────────────────────────────────────

SITEMAP_LABELS = {
    "page-sitemap.xml":                 ("Pages",                "All published WordPress pages"),
    "post-sitemap.xml":                 ("Blog Posts",           "All published blog posts"),
    "gary-birthday-wishes-sitemap.xml": ("Gary Birthday Wishes", "Custom post type — birthday messages for Gary"),
    "linda-memories-sitemap.xml":       ("Linda Memories",       "Custom post type — tributes for Linda Francis"),
    "category-sitemap.xml":             ("Categories",           "Blog category archive pages"),
    "post_tag-sitemap.xml":             ("Post Tags",            "Blog tag archive pages"),
    "chapters-sitemap.xml":             ("Chapters",             "Custom post type — book chapters"),
    "jou-sitemap.xml":                  ("JOU Content",          "Custom post type — JOU section"),
    "audio-clips-sitemap.xml":          ("Audio Clips",          "Custom post type — audio content"),
    "elementor-hf-sitemap.xml":         ("Elementor Templates",  "Internal Elementor header/footer templates (not public pages)"),
    "author-sitemap.xml":               ("Author Archives",      "Author archive pages"),
}

def parse_sitemap_entries(xml_body):
    entries = []
    for block in re.findall(r"<url>(.*?)</url>", xml_body, re.DOTALL):
        loc = re.search(r"<loc>\s*(https?://[^\s<]+)\s*</loc>", block)
        lm  = re.search(r"<lastmod>\s*([^\s<]+)\s*</lastmod>", block)
        if loc:
            url = loc.group(1).strip()
            entries.append({
                "url":     url,
                "path":    url.replace(BASE_URL, "") or "/",
                "lastmod": lm.group(1).strip() if lm else "",
            })
    return entries

def get_sitemaps():
    results, seen = {}, set()
    root, _ = fetch(f"{BASE_URL}/wp-sitemap.xml")
    if not root:
        root, _ = fetch(f"{BASE_URL}/sitemap_index.xml")
    if not root:
        return results
    for ns in re.findall(r"<loc>\s*(https?://[^\s<]+sitemap[^\s<]*)\s*</loc>", root):
        if ns in seen:
            continue
        seen.add(ns)
        nb, _ = fetch(ns)
        if nb:
            entries = parse_sitemap_entries(nb)
            name    = ns.split("/")[-1]
            label, desc = SITEMAP_LABELS.get(name, (name.replace("-sitemap.xml","").title(), ""))
            results[name] = {"count": len(entries), "src": ns,
                             "label": label, "desc": desc, "urls": entries}
    return results

# ── nav ───────────────────────────────────────────────────────────────────────

KNOWN_LABELS = {
    "": "Home", "/get-started": "Get Started", "/about": "About",
    "/about/seat-of-the-soul-institute": "About — Institute",
    "/about-gary-zukav": "About Gary Zukav",
    "/about-linda-francis": "About Linda Francis",
    "/remember-linda-homepage": "Remember Linda",
    "/podcast": "Podcast", "/failing-government": "Failing Government",
    "/ai-and-human-evolution": "AI & Human Evolution",
    "/soul-connections-newsletter": "Newsletter",
    "/books": "Books", "/apg-optin": "APG Opt-in", "/shop": "Shop",
}

def nav_label(url):
    path = url.replace(BASE_URL, "").rstrip("/")
    return KNOWN_LABELS.get(path, path.split("/")[-1].replace("-"," ").title() or "Home")

def get_nav():
    body, _ = fetch(BASE_URL)
    if not body:
        return [BASE_URL]
    nav_blocks = re.findall(r"<nav[\s>].*?</nav>", body, re.DOTALL | re.IGNORECASE)
    search_in  = nav_blocks if nav_blocks else [body]
    href_re    = re.compile(r'href=["\'](' + re.escape(BASE_URL) + r'[^"\'#]*)["\']')
    seen, out  = set(), []
    for block in search_in:
        for url in href_re.findall(block):
            clean = url.rstrip("/")
            if clean not in seen:
                seen.add(clean)
                out.append(clean)
    if BASE_URL not in out:
        out.insert(0, BASE_URL)
    return out

# ── page classification ───────────────────────────────────────────────────────

def normalize_title(t):
    t = re.sub(r'&[a-zA-Z0-9#]+;', ' ', t)
    t = re.sub(r'<[^>]+>', '', t)
    return re.sub(r'\s+', ' ', t).strip().lower()

def classify_page(slug):
    s = slug.lower()

    # Thank You / Confirmation (check first)
    if any(k in s for k in ['-ty', '-thank-you', 'thank-you', 'thankyou',
                             'message-to-linda-received', 'registration-received',
                             'linda-celebration-thank']):
        return 'Thank You'

    # System / Membership
    if s in ('sg', 'style-sheet', 'evening-welcome', 'email-series-update') or \
       any(k in s for k in ['cart', 'checkout', 'my-account', 'soul2soul', 'your-profile',
                             'opt-out', 'privacy-policy', 'refund-cancel', 'terms-of-use']):
        return 'System'

    # Program / Event
    if any(k in s for k in ['registration', 'waitlist', 'questionnaire', 'optin',
                             'apsp', 'spp-', 'spt-', 'jou23', 'jtts', 'lav-terms',
                             'beyond-the-five-senses', 'cultivatingemotional',
                             'intuitivemultisensory', 'daily-intuition-practice',
                             'listen-in', 'listen-with-gary', 'mutli-five',
                             'cultivating-love', 'fear-evaluation', 'love-evaluation',
                             'join-the-waitlist', 'garyzukavlive', 'video-april',
                             'universal-human-audiobook', 'universal-human-celebrates',
                             'join-seat-of-the-soul-team', 'seat-of-the-soul-career',
                             '33rd-anniversary', 'ground-rules', 'garys-welcome',
                             'apg-optin', 'event-waitlist', 'journey-questionnaire',
                             'authentic-power-support-program',
                             'journey-to-the-soul-questionnaire']):
        return 'Program / Event'

    # Content
    if any(k in s for k in ['universalhuman', 'heartofthesoul', 'for-linda',
                             'linda-celebrat', 'linda-francis-celebrat',
                             'lindas-mailbox', 'messages-for-linda',
                             'happy-birthday', 'wishes-for-gary', 'paulo-coelhos',
                             'multi-sensory-vocab', 'responsible-choice',
                             'love-fear', 'judgment', 'addiction',
                             'gifts-of-the-pandemic', 'share-your-favorite',
                             'subscribe-to-podcast', 'free-tools',
                             'questions-and-answers', 'seat-of-the-soul-33rd']):
        return 'Content'

    return 'Main Site'

# ── data builders ─────────────────────────────────────────────────────────────

def build_page_data(pages):
    # detect duplicates by normalized title
    title_count = {}
    for p in pages:
        nt = normalize_title(title_text(p))
        title_count[nt] = title_count.get(nt, 0) + 1

    rows = []
    for p in sorted(pages, key=lambda x: x.get("slug","")):
        slug = p.get("slug","")
        rd, rm = p.get("date",""), p.get("modified","")
        t  = title_text(p)
        rows.append({"id": p.get("id",""), "slug": slug,
                     "url": f"{BASE_URL}/{slug}", "title": t,
                     "published": fmt_date(rd), "pub_iso": rd[:10] if rd else "",
                     "modified":  fmt_date(rm), "mod_iso": rm[:10] if rm else "",
                     "category":  classify_page(slug),
                     "year":      rd[:4] if rd else "",
                     "is_dup":    title_count.get(normalize_title(t), 0) > 1})
    return rows

def build_post_data(posts):
    rows = []
    for p in sorted(posts, key=lambda x: x.get("date",""), reverse=True):
        slug = p.get("slug","")
        rd, rm = p.get("date",""), p.get("modified","")
        rows.append({"id": p.get("id",""), "slug": slug,
                     "url": f"{BASE_URL}/{slug}", "title": title_text(p),
                     "published": fmt_date(rd), "pub_iso": rd[:10] if rd else "",
                     "modified":  fmt_date(rm), "mod_iso": rm[:10] if rm else ""})
    return rows

# ── HTML fragments ────────────────────────────────────────────────────────────

def render_nav_cards(nav):
    cards = []
    for i, url in enumerate(nav):
        label  = nav_label(url)
        path   = url.replace(BASE_URL,"") or "/"
        active = " active" if i == 0 else ""
        cards.append(
            f'<div class="nc{active}" onclick="loadPreview(\'{url}\',this)" data-url="{url}">'
            f'<div class="nc-row"><span class="nc-label">{label}</span>'
            f'<a class="nc-ext" href="{url}" target="_blank" onclick="event.stopPropagation()">&#8599;</a></div>'
            f'<span class="nc-path">{path}</span></div>'
        )
    return "\n".join(cards)

def render_sitemap_tiles(sm):
    tiles = []
    for name, data in sorted(sm.items(), key=lambda x: -x[1]["count"]):
        name_esc = name.replace("'", "\\'")
        tiles.append(
            f'<div class="sm-tile" data-name="{name}" onclick="openSitemap(\'{name_esc}\',this)">'
            f'<div class="sm-tile-left">'
            f'<span class="sm-tile-label">{data["label"]}</span>'
            f'<span class="sm-tile-file">{name}</span>'
            f'<span class="sm-tile-desc">{data["desc"]}</span>'
            f'</div>'
            f'<div class="sm-tile-right">'
            f'<span class="sm-tile-count">{data["count"]}</span>'
            f'<span class="sm-tile-hint">Explore &#8594;</span>'
            f'</div></div>'
        )
    return "\n".join(tiles)

# ── HTML template (plain string — no f-string brace conflicts) ────────────────

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
  <title>SOTSI Site Audit — seatofthesoul.com</title>
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
  <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;500;600;700;800&family=Quicksand:wght@600;700&display=swap" rel="stylesheet"/>
  <link href="https://unpkg.com/tabulator-tables@6.3.0/dist/css/tabulator.min.css" rel="stylesheet"/>
  <script src="https://unpkg.com/tabulator-tables@6.3.0/dist/js/tabulator.min.js"></script>
  <style>
    /* ── tokens (Luno dashboard palette) ───────────────── */
    :root {
      --bg:       #f4f5f7;
      --surface:  #ffffff;
      --navy:     #1c2333;
      --navy2:    #243049;
      --primary:  #405189;
      --primary2: #3644a0;
      --muted:    #878a99;
      --text:     #212529;
      --border:   #e9ebec;
      --success:  #0ab39c;
      --danger:   #f06548;
      --warning:  #f7b84b;
      --info:     #299cdb;
      --purple:   #7367f0;
      --shadow:   0 1px 3px rgba(56,65,74,.12);
      --shadow-h: 0 4px 12px rgba(56,65,74,.16);
      --r:        8px;
      --t:        all .2s ease;
      --font:     'Nunito', 'Open Sans', sans-serif;
      --font-qs:  'Quicksand', sans-serif;
    }
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: var(--font);
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
    }

    /* ── layout ──────────────────────────────────────────── */
    .page-header {
      background: var(--navy);
      padding: 1.25rem 2rem;
      display: flex; align-items: center; justify-content: space-between;
      flex-wrap: wrap; gap: 1rem;
    }
    .ph-brand { display: flex; flex-direction: column; gap: .15rem; }
    .ph-brand h1 {
      font-family: var(--font-qs);
      font-size: 1.25rem; font-weight: 700;
      color: #fff; letter-spacing: .01em;
    }
    .ph-brand .ph-url {
      font-size: .75rem; color: rgba(255,255,255,.45);
      font-family: monospace;
    }
    .ph-brand .ph-url a { color: rgba(255,255,255,.6); text-decoration: none; }
    .ph-brand .ph-url a:hover { color: #fff; }
    .ph-meta { font-size: .75rem; color: rgba(255,255,255,.5); text-align: right; line-height: 1.6; }
    .ph-meta strong { color: rgba(255,255,255,.8); }

    .page-body { padding: 1.5rem 2rem 4rem; max-width: 1500px; margin: 0 auto; }

    /* ── KPI cards ───────────────────────────────────────── */
    .kpi-row {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
      gap: 1rem; margin-bottom: 1.75rem;
    }
    .kpi {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--r);
      box-shadow: var(--shadow);
      padding: 1.1rem 1.25rem;
      display: flex; align-items: center; gap: 1rem;
      transition: var(--t);
    }
    .kpi:hover { box-shadow: var(--shadow-h); }
    .kpi-icon {
      width: 46px; height: 46px; border-radius: 8px;
      display: flex; align-items: center; justify-content: center;
      flex-shrink: 0; font-size: 1.2rem; font-weight: 700;
    }
    .kpi-icon.green  { background: rgba(10,179,156,.12); color: var(--success); }
    .kpi-icon.danger { background: rgba(240,101,72,.12); color: var(--danger); }
    .kpi-icon.blue   { background: rgba(64,81,137,.12);  color: var(--primary); }
    .kpi-icon.yellow { background: rgba(247,184,75,.15); color: #c9950a; }
    .kpi-icon.info   { background: rgba(41,156,219,.12); color: var(--info); }
    .kpi-body { min-width: 0; }
    .kpi-label { font-size: .7rem; font-weight: 700; text-transform: uppercase;
                 letter-spacing: .07em; color: var(--muted); margin-bottom: .15rem; }
    .kpi-val   { font-size: 1.7rem; font-weight: 800; line-height: 1; color: var(--text);
                 letter-spacing: -.02em; }
    .kpi-sub   { font-size: .7rem; color: var(--muted); margin-top: .2rem; }

    /* ── tabs (Luno underline style) ─────────────────────── */
    .tab-bar {
      display: flex; gap: 0;
      border-bottom: 1px solid var(--border);
      margin-bottom: 1.5rem; flex-wrap: wrap;
    }
    .tab-btn {
      font-family: var(--font); font-size: .875rem; font-weight: 500;
      padding: .625rem 1.1rem; border: none;
      border-bottom: 2px solid transparent; margin-bottom: -1px;
      background: transparent; color: var(--muted);
      cursor: pointer; transition: var(--t); white-space: nowrap;
    }
    .tab-btn:hover { color: var(--text); }
    .tab-btn.active { color: var(--primary); border-bottom-color: var(--primary); font-weight: 700; }
    .tab-count {
      display: inline-flex; align-items: center; justify-content: center;
      font-size: .67rem; font-weight: 700;
      background: rgba(64,81,137,.1); color: var(--primary);
      padding: .05rem .4rem; border-radius: 4px; margin-left: .35rem;
    }
    .tab-btn.active .tab-count { background: var(--primary); color: #fff; }
    .tab-btn.danger-tab.active { color: var(--danger); border-bottom-color: var(--danger); }
    .tab-btn.danger-tab.active .tab-count { background: var(--danger); }
    .tab-btn.danger-tab .tab-count { background: rgba(240,101,72,.1); color: var(--danger); }

    .tab-panel { display: none; animation: fadeUp .22s ease forwards; }
    .tab-panel.active { display: block; }
    @keyframes fadeUp {
      from { opacity: 0; transform: translateY(8px); }
      to   { opacity: 1; transform: translateY(0); }
    }

    /* ── card wrapper ─────────────────────────────────────── */
    .card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--r);
      box-shadow: var(--shadow);
    }
    .card-header {
      padding: .875rem 1.25rem;
      border-bottom: 1px solid var(--border);
      display: flex; align-items: center; justify-content: space-between;
      gap: .75rem;
    }
    .card-header h2 { font-size: .95rem; font-weight: 700; color: var(--text); }
    .card-header .ch-meta { font-size: .78rem; color: var(--muted); }
    .card-body { padding: 1.25rem; }

    /* ── search bar ───────────────────────────────────────── */
    .search-bar { display: flex; align-items: center; gap: .75rem; margin-bottom: 1rem; flex-wrap: wrap; }
    .search-input {
      font-family: var(--font); font-size: .875rem;
      padding: .45rem 1rem; border: 1px solid var(--border);
      border-radius: 6px; background: var(--surface); color: var(--text);
      outline: none; transition: var(--t); width: 280px;
    }
    .search-input::placeholder { color: var(--muted); }
    .search-input:focus { border-color: var(--primary); box-shadow: 0 0 0 3px rgba(64,81,137,.1); }
    .search-hint { font-size: .78rem; color: var(--muted); }

    /* ── Tabulator Luno theme override ───────────────────── */
    .tabulator {
      background: var(--surface);
      border: 1px solid var(--border) !important;
      border-radius: var(--r);
      box-shadow: var(--shadow);
      font-family: var(--font);
      font-size: .84rem;
    }
    .tabulator .tabulator-header { background: var(--surface); border-bottom: 1px solid var(--border) !important; }
    .tabulator .tabulator-header .tabulator-col {
      background: var(--surface);
      border-right: 1px solid var(--border) !important;
    }
    .tabulator .tabulator-header .tabulator-col .tabulator-col-title {
      color: var(--muted);
      font-size: .7rem; font-weight: 700;
      text-transform: uppercase; letter-spacing: .06em;
    }
    .tabulator .tabulator-header .tabulator-col.tabulator-sortable:hover { background: #f8f9fa; }
    .tabulator .tabulator-header .tabulator-col .tabulator-arrow { border-bottom-color: var(--muted) !important; }
    .tabulator-row { background: var(--surface); border-bottom: 1px solid var(--border); transition: background .12s; }
    .tabulator-row:hover { background: rgba(64,81,137,.04) !important; }
    .tabulator-row .tabulator-cell {
      border-right: 1px solid var(--border);
      padding: .6rem 1rem; color: var(--text);
    }
    .tabulator-row .tabulator-cell:last-child { border-right: none; }
    .tabulator-scrollHolder { overflow-y: auto !important; }
    .tabulator .tabulator-tableholder { overflow-y: auto !important; }
    .t-link  { color: var(--primary); text-decoration: none; font-family: monospace; font-size: .79rem; }
    .t-id    { color: var(--muted); font-size: .73rem; }
    .t-muted { color: var(--muted); font-size: .78rem; }
    .t-title { font-weight: 600; }
    .t-ext-btn {
      display: inline-block; margin-left: .45rem;
      font-size: .72rem; color: var(--primary);
      text-decoration: none; opacity: 0;
      transition: opacity .15s, background .12s;
      padding: .05rem .28rem; border-radius: 3px;
      vertical-align: middle;
    }
    .tabulator-row:hover .t-ext-btn { opacity: 1; }
    .t-ext-btn:hover { background: var(--primary); color: #fff; }
    .badge {
      display: inline-block; padding: .2rem .5rem;
      border-radius: 4px; font-size: .68rem; font-weight: 700;
      text-transform: uppercase; letter-spacing: .04em;
    }
    .badge-draft   { background: rgba(135,138,153,.12); color: var(--muted); }
    .badge-private { background: rgba(41,156,219,.12);  color: var(--info); }

    /* ── nav tab ─────────────────────────────────────────── */
    .nav-layout {
      display: grid; grid-template-columns: 260px 1fr;
      gap: 1rem; align-items: start;
    }
    .nc-col {
      display: flex; flex-direction: column; gap: .4rem;
      max-height: 580px; overflow-y: auto; padding-right: .2rem;
    }
    .nc-col::-webkit-scrollbar { width: 3px; }
    .nc-col::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

    .nc {
      background: var(--surface); border: 1px solid var(--border);
      border-left: 3px solid transparent;
      border-radius: var(--r); padding: .75rem .9rem;
      cursor: pointer; transition: var(--t);
    }
    .nc:hover { border-left-color: var(--primary); background: #f8f9fb; box-shadow: var(--shadow); }
    .nc.active { border-left-color: var(--primary); background: rgba(64,81,137,.05); }
    .nc-row { display: flex; justify-content: space-between; align-items: flex-start; gap: .5rem; }
    .nc-label { font-weight: 700; font-size: .875rem; color: var(--text); }
    .nc-path  { font-family: monospace; font-size: .71rem; color: var(--muted); display: block; margin-top: .2rem; }
    .nc-ext   {
      font-size: .72rem; color: var(--primary); text-decoration: none;
      opacity: 0; flex-shrink: 0; padding: .1rem .3rem;
      border-radius: 4px; transition: var(--t);
    }
    .nc:hover .nc-ext, .nc.active .nc-ext { opacity: 1; }
    .nc-ext:hover { background: var(--primary); color: #fff; }

    /* ── iframe panel ────────────────────────────────────── */
    .preview-wrap {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--r);
      box-shadow: var(--shadow);
      overflow: hidden;
      position: sticky; top: 1rem;
    }
    .preview-chrome {
      background: var(--navy);
      padding: .55rem .9rem;
      display: flex; align-items: center; gap: .6rem;
    }
    .chrome-dots { display: flex; gap: .28rem; }
    .chrome-dots span { width: 10px; height: 10px; border-radius: 50%; }
    .chrome-dots span:nth-child(1) { background: #ff5f57; }
    .chrome-dots span:nth-child(2) { background: #ffbd2e; }
    .chrome-dots span:nth-child(3) { background: #28c840; }
    .chrome-url {
      flex: 1; background: rgba(255,255,255,.07); border-radius: 5px;
      padding: .22rem .7rem; font-family: monospace; font-size: .7rem;
      color: rgba(255,255,255,.55); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }
    .chrome-open {
      font-size: .7rem; color: rgba(176,165,244,.8); text-decoration: none;
      white-space: nowrap; font-weight: 600; transition: var(--t);
    }
    .chrome-open:hover { color: #fff; }
    .preview-body { position: relative; }
    #preview-frame { width: 100%; height: 500px; border: none; display: block; transition: opacity .2s; }

    /* iframe loading spinner */
    .iframe-loader {
      position: absolute; inset: 0; z-index: 10;
      background: var(--bg);
      display: flex; flex-direction: column;
      align-items: center; justify-content: center; gap: .75rem;
      transition: opacity .25s;
    }
    .iframe-loader.done { opacity: 0; pointer-events: none; }
    .spin-ring {
      width: 36px; height: 36px; border-radius: 50%;
      border: 3px solid var(--border);
      border-top-color: var(--primary);
      animation: spin .7s linear infinite;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
    .spin-label { font-size: .78rem; color: var(--muted); }

    .preview-blocked {
      display: none; position: absolute; inset: 0; z-index: 9;
      background: var(--bg); flex-direction: column;
      align-items: center; justify-content: center;
      gap: 1rem; padding: 2rem; text-align: center;
    }
    .preview-blocked.show { display: flex; }
    .preview-blocked p { font-size: .84rem; color: var(--muted); max-width: 260px; line-height: 1.5; }
    .preview-blocked a {
      background: var(--primary); color: #fff;
      padding: .45rem 1.4rem; border-radius: 6px;
      text-decoration: none; font-size: .8rem; font-weight: 700; transition: var(--t);
    }
    .preview-blocked a:hover { background: var(--primary2); }

    /* ── sitemap tiles ───────────────────────────────────── */
    .sm-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(290px, 1fr));
      gap: .75rem; margin-bottom: 1rem;
    }
    .sm-tile {
      background: var(--surface); border: 1px solid var(--border);
      border-left: 3px solid var(--border);
      border-radius: var(--r); padding: .9rem 1.1rem;
      display: flex; justify-content: space-between; align-items: center; gap: 1rem;
      box-shadow: var(--shadow); cursor: pointer; transition: var(--t);
    }
    .sm-tile:hover { border-left-color: var(--primary); box-shadow: var(--shadow-h); }
    .sm-tile.active { border-left-color: var(--primary); background: rgba(64,81,137,.04); }
    .sm-tile-left { display: flex; flex-direction: column; gap: .15rem; min-width: 0; }
    .sm-tile-label { font-weight: 700; font-size: .88rem; color: var(--text); }
    .sm-tile-file  { font-family: monospace; font-size: .7rem; color: var(--muted); }
    .sm-tile-desc  { font-size: .72rem; color: var(--muted); line-height: 1.3; margin-top: .1rem; }
    .sm-tile-right { display: flex; flex-direction: column; align-items: flex-end; gap: .2rem; flex-shrink: 0; }
    .sm-tile-count { font-size: 1.6rem; font-weight: 800; color: var(--primary); letter-spacing: -.02em; line-height: 1; }
    .sm-tile-hint  { font-size: .65rem; color: var(--muted); }
    .sm-tile.active .sm-tile-hint { color: var(--primary); font-weight: 600; }

    /* ── sitemap expand panel ────────────────────────────── */
    .sm-panel {
      background: var(--surface); border: 1px solid var(--border);
      border-radius: var(--r); box-shadow: var(--shadow);
      margin-top: .75rem; overflow: hidden;
      max-height: 0; opacity: 0;
      transition: max-height .38s ease, opacity .28s ease;
      pointer-events: none;
    }
    .sm-panel.open { max-height: 700px; opacity: 1; pointer-events: all; }
    .sm-panel-header {
      background: var(--navy); padding: .85rem 1.25rem;
      display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: .75rem;
    }
    .sph-info { display: flex; flex-direction: column; gap: .15rem; }
    .sph-label { font-family: var(--font-qs); font-size: .95rem; font-weight: 700; color: #fff; }
    .sph-desc  { font-size: .73rem; color: rgba(255,255,255,.45); }
    .sph-actions { display: flex; align-items: center; gap: .6rem; }
    .sph-count {
      background: rgba(64,81,137,.5); color: rgba(255,255,255,.9);
      font-size: .72rem; font-weight: 700;
      padding: .2rem .65rem; border-radius: 4px;
    }
    .sph-xml {
      font-size: .72rem; color: rgba(176,165,244,.8);
      text-decoration: none; font-weight: 600;
      padding: .2rem .45rem; border-radius: 4px; transition: var(--t);
    }
    .sph-xml:hover { background: rgba(255,255,255,.1); color: #fff; }
    .sph-close {
      background: rgba(255,255,255,.08); border: none; color: rgba(255,255,255,.6);
      width: 26px; height: 26px; border-radius: 4px; cursor: pointer;
      font-size: .85rem; display: flex; align-items: center; justify-content: center;
      transition: var(--t);
    }
    .sph-close:hover { background: rgba(255,255,255,.16); color: #fff; }
    .sm-panel-body { padding: 1rem 1.25rem 1.25rem; }

    /* ── sitemap total bar ───────────────────────────────── */
    .sm-total {
      background: var(--navy); border-radius: var(--r);
      padding: .85rem 1.25rem; margin-top: .75rem;
      display: flex; justify-content: space-between; align-items: center;
    }
    .sm-total span:first-child { font-size: .82rem; color: rgba(255,255,255,.55); }
    .sm-total-val { font-size: 1.2rem; font-weight: 800; color: #fff; }

    /* ── footer ──────────────────────────────────────────── */
    .rpt-footer {
      margin-top: 3rem; padding-top: 1.25rem; border-top: 1px solid var(--border);
      font-size: .75rem; color: var(--muted);
      display: flex; justify-content: space-between; flex-wrap: wrap; gap: .5rem;
    }

    /* ── classification tab ─────────────────────────────────── */
    .cc-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: .75rem; margin-bottom: 1.25rem;
    }
    .cc {
      background: var(--surface); border: 1px solid var(--border);
      border-top: 3px solid var(--border);
      border-radius: var(--r); box-shadow: var(--shadow);
      padding: 1rem 1.1rem; cursor: pointer;
      transition: var(--t);
    }
    .cc:hover, .cc.active { border-top-color: var(--cc-color); box-shadow: var(--shadow-h); }
    .cc.active { background: rgba(0,0,0,.015); }
    .cc-count { font-size: 2rem; font-weight: 800; letter-spacing: -.03em;
                color: var(--cc-color); line-height: 1; }
    .cc-label { font-size: .72rem; font-weight: 700; text-transform: uppercase;
                letter-spacing: .06em; color: var(--muted); margin-top: .3rem; }

    .cat-filter-row { display: flex; gap: .4rem; flex-wrap: wrap; align-items: center; }
    .cat-filter-btn {
      font-family: var(--font); font-size: .75rem; font-weight: 600;
      padding: .3rem .8rem; border-radius: 99px; cursor: pointer;
      border: 1px solid var(--border); background: var(--surface);
      color: var(--muted); transition: var(--t);
    }
    .cat-filter-btn:hover { border-color: currentColor; }
    .cat-filter-btn.active { color: #fff; border-color: transparent; }

    /* ── triage tab ─────────────────────────────────────────── */
    .tri-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
      gap: .75rem;
    }
    .tri-card {
      background: var(--surface); border: 1px solid var(--border);
      border-left: 4px solid var(--cc-color); border-radius: var(--r);
      box-shadow: var(--shadow); padding: 1rem 1.1rem; cursor: pointer;
      transition: var(--t);
    }
    .tri-card:hover, .tri-card.active { box-shadow: var(--shadow-h); }
    .tri-card.active { background: rgba(0,0,0,.02); }
    .tri-count { font-size: 1.9rem; font-weight: 800; color: var(--cc-color);
                 line-height: 1; letter-spacing: -.03em; }
    .tri-label { font-size: .72rem; font-weight: 700; text-transform: uppercase;
                 letter-spacing: .06em; color: var(--muted); margin-top: .3rem; }
    .tri-sub   { font-size: .68rem; color: var(--muted); margin-top: .2rem; line-height: 1.4; }

    .verdict-badge {
      display: inline-block; padding: .2rem .55rem; border-radius: 4px;
      font-size: .68rem; font-weight: 800; letter-spacing: .04em;
      text-transform: uppercase; white-space: nowrap;
    }
    .verdict-keep  { background: rgba(10,179,156,.12);  color: #0ab39c; }
    .verdict-drop  { background: rgba(240,101,72,.12);  color: #f06548; }
    .verdict-review{ background: rgba(247,184,75,.15);  color: #c9950a; }
    .tab-btn.triage-tab.active { color: #0ab39c; border-bottom-color: #0ab39c; }
    .tab-btn.triage-tab.active .tab-count { background: #0ab39c; color: #fff; }
    .tab-btn.triage-tab .tab-count { background: rgba(10,179,156,.15); color: #0ab39c; }

    .flag-chip {
      display: inline-block; padding: .12rem .4rem; border-radius: 3px;
      font-size: .62rem; font-weight: 600; background: rgba(64,81,137,.08);
      color: var(--primary); margin-right: .25rem; margin-bottom: .15rem;
    }
    .flag-chip.warn { background: rgba(247,184,75,.16); color: #c9950a; }
    .flag-chip.bad  { background: rgba(240,101,72,.12); color: #f06548; }

    /* ── summary category modal ─────────────────────────────── */
    .sum-backdrop {
      position: fixed; inset: 0; z-index: 1100;
      background: rgba(28,35,51,.48);
      opacity: 0; pointer-events: none;
      transition: opacity .25s;
    }
    .sum-backdrop.open { opacity: 1; pointer-events: all; }

    .sum-modal {
      position: fixed; top: 50%; left: 50%;
      transform: translate(-50%,-48%) scale(.97);
      width: min(880px, 92vw); max-height: 82vh;
      background: var(--surface); border-radius: var(--r);
      box-shadow: 0 12px 48px rgba(28,35,51,.28);
      display: flex; flex-direction: column;
      z-index: 1101; opacity: 0; pointer-events: none;
      transition: opacity .22s, transform .22s cubic-bezier(.22,1,.36,1);
    }
    .sum-modal.open { opacity: 1; pointer-events: all; transform: translate(-50%,-50%) scale(1); }

    .sum-modal-hdr {
      background: var(--navy); padding: .9rem 1.25rem;
      display: flex; align-items: center; justify-content: space-between;
      border-radius: var(--r) var(--r) 0 0; flex-shrink: 0;
    }
    .sum-modal-title { display: flex; align-items: center; gap: .75rem; }
    .sum-modal-cat {
      font-family: var(--font-qs); font-size: 1rem; font-weight: 700;
    }
    .sum-modal-cnt { font-size: .78rem; color: rgba(255,255,255,.4); }
    .sum-modal-body {
      padding: 1rem 1.25rem 1.25rem;
      overflow: hidden; display: flex; flex-direction: column; gap: .75rem;
    }

    .ebd-row { cursor: default; }
    .ebd-row.clickable { cursor: pointer; transition: background .12s; border-radius: 6px; padding-left:.35rem; padding-right:.35rem; margin:0 -.35rem; }
    .ebd-row.clickable:hover { background: rgba(64,81,137,.06); }
    .ebd-row.clickable:hover .ebd-view { opacity: 1; }
    .ebd-view { font-size: .7rem; color: var(--primary); opacity: 0; transition: opacity .15s; margin-left: .4rem; flex-shrink:0; }

    /* ── executive summary tab ──────────────────────────────── */
    .exec-hero {
      display: grid; grid-template-columns: 1fr 1fr;
      gap: 1.5rem; margin-bottom: 1.25rem;
    }
    .exec-hero-left {
      background: var(--navy); border-radius: var(--r);
      padding: 2rem 2.25rem; display: flex; flex-direction: column; gap: .5rem;
    }
    .exec-eyebrow {
      font-size: .68rem; font-weight: 700; text-transform: uppercase;
      letter-spacing: .1em; color: rgba(255,255,255,.4);
    }
    .exec-big-num {
      font-family: var(--font-qs); font-size: 5rem; font-weight: 700;
      color: #fff; line-height: 1; letter-spacing: -.04em;
    }
    .exec-big-label {
      font-size: 1.1rem; font-weight: 700; color: rgba(255,255,255,.85);
    }
    .exec-hero-sub {
      font-size: .8rem; color: rgba(255,255,255,.4);
      line-height: 1.5; margin-top: .25rem; max-width: 300px;
    }
    .exec-right-col {
      display: flex; flex-direction: column; gap: .75rem;
    }
    .emc {
      background: var(--surface); border: 1px solid var(--border);
      border-radius: var(--r); box-shadow: var(--shadow);
      padding: 1rem 1.25rem;
      display: flex; align-items: center; justify-content: space-between;
      gap: 1rem; flex: 1;
    }
    .emc-info { display: flex; flex-direction: column; gap: .15rem; }
    .emc-label { font-size: .72rem; font-weight: 700; text-transform: uppercase;
                 letter-spacing: .06em; color: var(--muted); }
    .emc-sub   { font-size: .72rem; color: var(--muted); line-height: 1.4; }
    .emc-val   { font-size: 2.4rem; font-weight: 800; letter-spacing: -.03em;
                 line-height: 1; color: var(--text); flex-shrink: 0; }
    .emc-val.green  { color: var(--success); }
    .emc-val.blue   { color: var(--primary); }
    .emc-val.danger { color: var(--danger); }
    .emc-val.yellow { color: #c9950a; }

    .exec-breakdown { display: flex; flex-direction: column; gap: 0; }
    .ebd-row {
      display: flex; align-items: center; gap: 1.25rem;
      padding: .85rem 0; border-bottom: 1px solid var(--border);
    }
    .ebd-row:last-child { border-bottom: none; }
    .ebd-bar-wrap { flex: 1; height: 8px; background: var(--border); border-radius: 99px; overflow: hidden; }
    .ebd-bar      { height: 100%; border-radius: 99px; transition: width .6s ease; }
    .ebd-label    { font-size: .82rem; font-weight: 600; color: var(--text); width: 200px; flex-shrink: 0; }
    .ebd-val      { font-size: .88rem; font-weight: 800; color: var(--text); width: 44px; text-align: right; flex-shrink: 0; }
    .ebd-note     { font-size: .72rem; color: var(--muted); width: 240px; flex-shrink: 0; }

    .copy-btn {
      font-family: var(--font); font-size: .78rem; font-weight: 700;
      padding: .35rem 1rem; border-radius: 6px; cursor: pointer;
      border: 1px solid var(--primary); color: var(--primary);
      background: transparent; transition: var(--t);
    }
    .copy-btn:hover { background: var(--primary); color: #fff; }
    .copy-btn.copied { background: var(--success); border-color: var(--success); color: #fff; }

    .exec-copybox {
      font-family: monospace; font-size: .8rem; line-height: 1.7;
      color: var(--text); background: var(--bg);
      border: 1px solid var(--border); border-radius: 6px;
      padding: 1.1rem 1.25rem; white-space: pre-wrap; margin: 0;
      user-select: all;
    }

    @media (max-width: 768px) {
      .exec-hero { grid-template-columns: 1fr; }
      .ebd-note { display: none; }
    }

    /* ── row preview panel (slides in from right, half screen) ─ */
    .rp-backdrop {
      position: fixed; inset: 0; z-index: 1000;
      background: rgba(28,35,51,.38);
      opacity: 0; pointer-events: none;
      transition: opacity .28s ease;
    }
    .rp-backdrop.open { opacity: 1; pointer-events: all; }

    .row-panel {
      position: fixed; top: 0; right: 0;
      width: 50%; height: 100vh; z-index: 1001;
      background: var(--surface);
      box-shadow: -6px 0 32px rgba(28,35,51,.22);
      display: flex; flex-direction: column;
      transform: translateX(100%);
      transition: transform .34s cubic-bezier(.22,1,.36,1);
    }
    .row-panel.open { transform: translateX(0); }

    .rp-chrome {
      background: var(--navy); padding: .65rem 1rem;
      display: flex; align-items: center; gap: .75rem; flex-shrink: 0;
    }
    .rp-dots { display: flex; gap: .28rem; }
    .rp-dots span { width: 10px; height: 10px; border-radius: 50%; }
    .rp-dots span:nth-child(1) { background: #ff5f57; }
    .rp-dots span:nth-child(2) { background: #ffbd2e; }
    .rp-dots span:nth-child(3) { background: #28c840; }
    .rp-info { flex: 1; min-width: 0; }
    .rp-title-bar {
      font-size: .73rem; font-weight: 700; color: rgba(255,255,255,.8);
      white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }
    .rp-url-bar {
      font-family: monospace; font-size: .65rem;
      color: rgba(255,255,255,.38);
      white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }
    .rp-actions { display: flex; align-items: center; gap: .35rem; flex-shrink: 0; }
    .rp-ext {
      font-size: .7rem; color: rgba(176,165,244,.85);
      text-decoration: none; font-weight: 600;
      padding: .2rem .5rem; border-radius: 4px; transition: var(--t);
      white-space: nowrap;
    }
    .rp-ext:hover { background: rgba(255,255,255,.1); color: #fff; }
    .rp-close {
      background: rgba(255,255,255,.08); border: none;
      color: rgba(255,255,255,.65); width: 28px; height: 28px;
      border-radius: 4px; cursor: pointer; font-size: .88rem;
      display: flex; align-items: center; justify-content: center;
      transition: var(--t); flex-shrink: 0;
    }
    .rp-close:hover { background: var(--danger); color: #fff; }

    .rp-body { flex: 1; position: relative; overflow: hidden; }
    .rp-loader {
      position: absolute; inset: 0; z-index: 10;
      background: var(--bg);
      display: flex; flex-direction: column;
      align-items: center; justify-content: center; gap: .75rem;
      transition: opacity .25s;
    }
    .rp-loader.done { opacity: 0; pointer-events: none; }
    .rp-frame { width: 100%; height: 100%; border: none; display: block; transition: opacity .2s; }
    .rp-blocked {
      display: none; position: absolute; inset: 0; z-index: 9;
      background: var(--bg); flex-direction: column;
      align-items: center; justify-content: center;
      gap: 1rem; padding: 2rem; text-align: center;
    }
    .rp-blocked.show { display: flex; }
    .rp-blocked p { font-size: .84rem; color: var(--muted); max-width: 260px; line-height: 1.5; }
    .rp-blocked a {
      background: var(--primary); color: #fff;
      padding: .45rem 1.4rem; border-radius: 6px;
      text-decoration: none; font-size: .8rem; font-weight: 700; transition: var(--t);
    }
    .rp-blocked a:hover { background: var(--primary2); }

    /* row cursor hint */
    .tabulator-row { cursor: pointer; }

    @media print {
      .tab-bar, .preview-wrap, .search-input, .sm-panel, .iframe-loader,
      .row-panel, .rp-backdrop { display: none !important; }
      .tab-panel { display: block !important; }
      body { background: #fff; }
      .page-body { padding: 1rem; }
    }
  </style>
</head>
<body>

<header class="page-header">
  <div class="ph-brand">
    <h1>WordPress Site Audit</h1>
    <div class="ph-url"><a href="__BASE_URL__" target="_blank">__BASE_URL_CLEAN__</a></div>
  </div>
  <div class="ph-meta">
    Report date: <strong>__TODAY__</strong><br>
    Source: WP REST API &amp; Sitemap XML
  </div>
</header>

<div class="page-body">

<!-- KPI CARDS -->
<div class="kpi-row">
  <div class="kpi">
    <div class="kpi-icon green">__N_PAGES__</div>
    <div class="kpi-body">
      <div class="kpi-label">Active Pages</div>
      <div class="kpi-val">__N_PAGES__</div>
      <div class="kpi-sub">status = publish</div>
    </div>
  </div>
  <div class="kpi">
    <div class="kpi-icon danger">__N_DRAFTS__</div>
    <div class="kpi-body">
      <div class="kpi-label">Draft Pages</div>
      <div class="kpi-val">__N_DRAFTS__</div>
      <div class="kpi-sub">from WP Admin</div>
    </div>
  </div>
  <div class="kpi">
    <div class="kpi-icon blue">__N_POSTS__</div>
    <div class="kpi-body">
      <div class="kpi-label">Blog Posts</div>
      <div class="kpi-val">__N_POSTS__</div>
      <div class="kpi-sub">published</div>
    </div>
  </div>
  <div class="kpi" style="cursor:pointer" onclick="document.querySelector('.tab-btn.triage-tab').click()">
    <div class="kpi-icon" style="background:rgba(10,179,156,.12);color:#0ab39c">__N_TRIAGE_KEEP__</div>
    <div class="kpi-body">
      <div class="kpi-label">Migration Triage</div>
      <div class="kpi-val"><span style="color:#0ab39c">__N_TRIAGE_KEEP__</span><span style="font-size:.7em;color:var(--muted);font-weight:500"> keep</span> · <span style="color:#f06548">__N_TRIAGE_DROP__</span><span style="font-size:.7em;color:var(--muted);font-weight:500"> drop</span></div>
      <div class="kpi-sub">click to review</div>
    </div>
  </div>
  <div class="kpi">
    <div class="kpi-icon yellow">__N_NAV__</div>
    <div class="kpi-body">
      <div class="kpi-label">Main Nav</div>
      <div class="kpi-val">__N_NAV__</div>
      <div class="kpi-sub">links detected</div>
    </div>
  </div>
  <div class="kpi">
    <div class="kpi-icon info">__TOTAL_SM__</div>
    <div class="kpi-body">
      <div class="kpi-label">Sitemap URLs</div>
      <div class="kpi-val">__TOTAL_SM__</div>
      <div class="kpi-sub">all content types</div>
    </div>
  </div>
</div>

<!-- TABS -->
<div class="tab-bar" role="tablist">
  <button class="tab-btn active" onclick="switchTab('summary',this)">
    Executive Summary
  </button>
  <button class="tab-btn" onclick="switchTab('nav',this)">
    Main Navigation <span class="tab-count">__N_NAV__</span>
  </button>
  <button class="tab-btn" onclick="switchTab('pages',this)">
    Active Pages <span class="tab-count">__N_PAGES__</span>
  </button>
  <button class="tab-btn" onclick="switchTab('classify',this)">
    Classification <span class="tab-count">__N_PAGES__</span>
  </button>
  <button class="tab-btn danger-tab" onclick="switchTab('drafts',this)">
    Draft Pages <span class="tab-count">__N_DRAFTS__</span>
  </button>
  <button class="tab-btn" onclick="switchTab('posts',this)">
    Blog Posts <span class="tab-count">__N_POSTS__</span>
  </button>
  <button class="tab-btn triage-tab" onclick="switchTab('triage',this)">
    Blog Migration Triage <span class="tab-count">__N_TRIAGE__</span>
  </button>
  <button class="tab-btn" onclick="switchTab('sitemap',this)">
    Sitemap Breakdown <span class="tab-count">__TOTAL_SM__</span>
  </button>
</div>

<!-- TAB: EXECUTIVE SUMMARY -->
<div id="tab-summary" class="tab-panel active">
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:1.25rem">

    <div class="card">
      <div class="card-header">
        <h2>Active Pages by Category</h2>
        <span class="ch-meta">__N_PAGES__ published pages</span>
      </div>
      <div class="card-body" id="sum-cat-body"></div>
    </div>

    <div class="card">
      <div class="card-header">
        <h2>Active Pages by Year Created</h2>
        <span class="ch-meta">when each page was first published</span>
      </div>
      <div class="card-body" id="sum-year-body"></div>
    </div>

  </div>
</div>

<!-- TAB: MAIN NAV -->
<div id="tab-nav" class="tab-panel">
  <div class="nav-layout">
    <div class="nc-col">__NAV_CARDS_HTML__</div>
    <div class="preview-wrap">
      <div class="preview-chrome">
        <div class="chrome-dots"><span></span><span></span><span></span></div>
        <div class="chrome-url" id="chrome-url">__FIRST_NAV__</div>
        <a class="chrome-open" id="chrome-open" href="__FIRST_NAV__" target="_blank">Open &#8599;</a>
      </div>
      <div class="preview-body">
        <div class="iframe-loader" id="iframe-loader">
          <div class="spin-ring"></div>
          <span class="spin-label">Loading preview&hellip;</span>
        </div>
        <iframe id="preview-frame" src="__FIRST_NAV__"
                sandbox="allow-same-origin allow-scripts allow-forms"
                title="Page preview"
                onload="onFrameLoad(this)" onerror="showBlocked()">
        </iframe>
        <div class="preview-blocked" id="blocked-msg">
          <p>This page can't be embedded here due to the site's X-Frame-Options policy.</p>
          <a id="blocked-link" href="__FIRST_NAV__" target="_blank">Open in new tab</a>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- TAB: ACTIVE PAGES -->
<div id="tab-pages" class="tab-panel">
  <div class="search-bar">
    <input class="search-input" id="pages-search" type="search" placeholder="Search by title or slug&hellip;"/>
    <span class="search-hint">__N_PAGES__ published pages &mdash; scroll to browse &mdash; click column header to sort</span>
  </div>
  <div id="pages-table"></div>
</div>

<!-- TAB: CLASSIFICATION -->
<div id="tab-classify" class="tab-panel">
  <div class="cc-grid" id="cc-grid">
    <!-- injected by JS -->
  </div>

  <div class="search-bar" style="margin-bottom:.75rem">
    <input class="search-input" id="classify-search" type="search" placeholder="Search title or slug&hellip;"/>
    <div class="cat-filter-row" id="cat-filter-row">
      <!-- injected by JS -->
    </div>
  </div>

  <div id="classify-table"></div>
</div>

<!-- TAB: DRAFT PAGES -->
<div id="tab-drafts" class="tab-panel">
  <div class="card" style="margin-bottom:1.25rem">
    <div class="card-header">
      <h2>Draft Pages <span class="tab-count" style="background:var(--danger);color:#fff">__N_DRAFTS__</span></h2>
      <span class="ch-meta">Not publicly visible &mdash; from WP Admin</span>
    </div>
    <div class="card-body">
      <div class="search-bar" style="margin-bottom:.75rem">
        <input class="search-input" id="drafts-search" type="search" placeholder="Search draft pages&hellip;"/>
      </div>
      <div id="drafts-table"></div>
    </div>
  </div>

  <div class="card">
    <div class="card-header">
      <h2>Draft Posts <span class="tab-count" style="background:var(--danger);color:#fff">__N_DRAFT_POSTS__</span></h2>
      <span class="ch-meta">Unpublished blog posts &mdash; from WP Admin</span>
    </div>
    <div class="card-body">
      <div class="search-bar" style="margin-bottom:.75rem">
        <input class="search-input" id="draft-posts-search" type="search" placeholder="Search draft posts&hellip;"/>
      </div>
      <div id="draft-posts-table"></div>
    </div>
  </div>
</div>

<!-- TAB: BLOG POSTS -->
<div id="tab-posts" class="tab-panel">
  <div class="search-bar">
    <input class="search-input" id="posts-search" type="search" placeholder="Search by title or slug&hellip;"/>
    <span class="search-hint">__N_POSTS__ published posts &mdash; sorted by publish date newest first</span>
  </div>
  <div id="posts-table"></div>
</div>

<!-- TAB: BLOG MIGRATION TRIAGE -->
<div id="tab-triage" class="tab-panel">
  <div class="card" style="margin-bottom:1.25rem">
    <div class="card-header">
      <h2>Blog Migration Triage</h2>
      <span class="ch-meta">Planning-only output &mdash; nothing here touches WordPress or the live site</span>
    </div>
    <div class="card-body">
      <div class="tri-grid" id="tri-grid"><!-- injected --></div>
    </div>
  </div>
  <div class="search-bar" style="margin-bottom:.75rem">
    <input class="search-input" id="triage-search" type="search" placeholder="Search title or slug&hellip;"/>
    <div class="cat-filter-row" id="tri-filter-row"><!-- injected --></div>
  </div>
  <div id="triage-table"></div>
</div>

<!-- TAB: SITEMAP -->
<div id="tab-sitemap" class="tab-panel">
  <div class="sm-grid">__SM_TILES_HTML__</div>

  <div class="sm-panel" id="sm-panel">
    <div class="sm-panel-header">
      <div class="sph-info">
        <span class="sph-label" id="sph-label">—</span>
        <span class="sph-desc"  id="sph-desc">—</span>
      </div>
      <div class="sph-actions">
        <span class="sph-count" id="sph-count">0 URLs</span>
        <a class="sph-xml" id="sph-xml" href="#" target="_blank">View XML &#8599;</a>
        <button class="sph-close" onclick="closeSitemap()" title="Close">&#x2715;</button>
      </div>
    </div>
    <div class="sm-panel-body">
      <div class="search-bar" style="margin-bottom:.75rem">
        <input class="search-input" id="sm-search" type="search" placeholder="Filter URLs&hellip;"/>
        <span class="search-hint">Click any row to open the URL in a new tab</span>
      </div>
      <div id="sm-table"></div>
    </div>
  </div>

  <div class="sm-total">
    <span>Total unique URLs across all sitemaps</span>
    <span class="sm-total-val">__TOTAL_SM__</span>
  </div>
</div>

<footer class="rpt-footer">
  <span>Generated __TODAY__ &middot; audit_sotsi.py &middot; 22D Marketing</span>
  <span>Print to PDF: Ctrl+P &rarr; Save as PDF &rarr; disable browser headers/footers</span>
</footer>

</div><!-- /page-body -->

<!-- SUMMARY CATEGORY MODAL -->
<div class="sum-backdrop" id="sum-backdrop" onclick="closeSumModal()"></div>
<div class="sum-modal" id="sum-modal">
  <div class="sum-modal-hdr">
    <div class="sum-modal-title">
      <span class="sum-modal-cat" id="sum-modal-cat"></span>
      <span class="sum-modal-cnt" id="sum-modal-cnt"></span>
    </div>
    <button class="rp-close" onclick="closeSumModal()" title="Close (Esc)">&#x2715;</button>
  </div>
  <div class="sum-modal-body">
    <input class="search-input" id="sum-modal-search" type="search" placeholder="Search title or slug&hellip;" style="width:100%"/>
    <div id="sum-modal-table"></div>
  </div>
</div>

<!-- ROW PREVIEW PANEL -->
<div class="rp-backdrop" id="rp-backdrop" onclick="closeRowPanel()"></div>
<div class="row-panel" id="row-panel">
  <div class="rp-chrome">
    <div class="rp-dots"><span></span><span></span><span></span></div>
    <div class="rp-info">
      <div class="rp-title-bar" id="rp-title"></div>
      <div class="rp-url-bar"   id="rp-url"></div>
    </div>
    <div class="rp-actions">
      <a class="rp-ext" id="rp-ext" href="#" target="_blank">Open &nearr;</a>
      <button class="rp-close" onclick="closeRowPanel()" title="Close (Esc)">&#x2715;</button>
    </div>
  </div>
  <div class="rp-body">
    <div class="rp-loader" id="rp-loader">
      <div class="spin-ring"></div>
      <span class="spin-label">Loading preview&hellip;</span>
    </div>
    <iframe class="rp-frame" id="rp-frame" src="about:blank"
            sandbox="allow-same-origin allow-scripts allow-forms"
            title="Row preview">
    </iframe>
    <div class="rp-blocked" id="rp-blocked">
      <p>This page can&rsquo;t be previewed here due to the site&rsquo;s X-Frame-Options policy.</p>
      <a id="rp-blocked-link" href="#" target="_blank">Open in new tab &nearr;</a>
    </div>
  </div>
</div>

<script>
const PAGES_DATA        = __PAGES_JSON__;
const POSTS_DATA        = __POSTS_JSON__;
const DRAFTS_DATA       = __DRAFTS_JSON__;
const DRAFT_POSTS_DATA  = __DRAFT_POSTS_JSON__;
const SITEMAP_DATA      = __SM_JSON__;
const TRIAGE_DATA       = __TRIAGE_JSON__;

// ── summary tab ────────────────────────────────────────────────────────────
function initSummary() {
  var catEl  = document.getElementById('sum-cat-body');
  var yearEl = document.getElementById('sum-year-body');
  if (catEl.children.length) return;

  var catColors = {
    'Main Site':'#405189','Program / Event':'#0ab39c',
    'Content':'#299cdb','System':'#878a99','Thank You':'#f7b84b'
  };
  var catCounts = {}, yearCounts = {};
  PAGES_DATA.forEach(function(d) {
    catCounts[d.category]  = (catCounts[d.category]  || 0) + 1;
    var y = d.year || 'Unknown';
    yearCounts[y] = (yearCounts[y] || 0) + 1;
  });

  var total = PAGES_DATA.length;

  function barRow(label, count, maxVal, color, clickable, color2) {
    var pct = Math.round(count / maxVal * 100);
    var cls = clickable ? ' clickable' : '';
    var data = clickable ? ' data-cat="' + label + '" data-color="' + color2 + '"' : '';
    return '<div class="ebd-row' + cls + '"' + data + '>'
      + '<span class="ebd-label" style="width:160px">' + label + '</span>'
      + '<div class="ebd-bar-wrap"><div class="ebd-bar" style="width:' + pct + '%;background:' + color + '"></div></div>'
      + '<span class="ebd-val">' + count + '</span>'
      + '<span class="ebd-note" style="width:52px;color:var(--muted);font-size:.72rem">' + Math.round(count / total * 100) + '%</span>'
      + (clickable ? '<span class="ebd-view">View &rarr;</span>' : '')
      + '</div>';
  }

  var catMax = Math.max.apply(null, Object.values(catCounts));
  var catHtml = '<div class="exec-breakdown">';
  Object.keys(catColors).forEach(function(k) {
    catHtml += barRow(k, catCounts[k] || 0, catMax, catColors[k], true, catColors[k]);
  });
  catEl.innerHTML = catHtml + '</div>';
  catEl.querySelectorAll('.ebd-row.clickable').forEach(function(row) {
    row.addEventListener('click', function() {
      openSumModal(this.dataset.cat, this.dataset.color);
    });
  });

  var yearKeys = Object.keys(yearCounts).sort();
  var yearMax  = Math.max.apply(null, Object.values(yearCounts));
  var yearHtml = '<div class="exec-breakdown">';
  yearKeys.forEach(function(y) {
    yearHtml += barRow(y, yearCounts[y], yearMax, 'var(--primary)', false);
  });
  yearEl.innerHTML = yearHtml + '</div>';
}

// ── summary category modal ─────────────────────────────────────────────────
var sumModalTable = null;

function openSumModal(cat, color) {
  var data = PAGES_DATA.filter(function(d) { return d.category === cat; });
  document.getElementById('sum-modal-cat').textContent = cat;
  document.getElementById('sum-modal-cat').style.color = color;
  document.getElementById('sum-modal-cnt').textContent = data.length + ' pages';
  document.getElementById('sum-modal-search').value = '';
  document.getElementById('sum-backdrop').classList.add('open');
  document.getElementById('sum-modal').classList.add('open');
  document.body.style.overflow = 'hidden';

  if (sumModalTable) {
    sumModalTable.replaceData(data);
    sumModalTable.clearFilter();
  } else {
    sumModalTable = new Tabulator('#sum-modal-table', {
      data: data, layout: 'fitColumns', height: 420,
      columns: [
        { title:'Title',     field:'title',   widthGrow:3, formatter:titleFmt,  sorter:'string' },
        { title:'Slug',      field:'slug',    widthGrow:2, formatter:slugFmt,   sorter:'string' },
        { title:'Published', field:'pub_iso', width:130, sorter:'date',
          sorterParams:{format:'YYYY-MM-DD'},
          formatter:function(c){ return dateFmt(c.getData().published); } },
        { title:'Modified',  field:'mod_iso', width:130, sorter:'date',
          sorterParams:{format:'YYYY-MM-DD'},
          formatter:function(c){ return dateFmt(c.getData().modified); } },
      ],
    });
    sumModalTable.on('rowClick', function(e, row) {
      var d = row.getData();
      closeSumModal();
      setTimeout(function(){ openRowPanel(d.url, d.title); }, 260);
    });
    document.getElementById('sum-modal-search').addEventListener('input', function() {
      var v = this.value.toLowerCase();
      if (!v) { sumModalTable.clearFilter(); return; }
      sumModalTable.setFilter(function(d) {
        return d.title.toLowerCase().includes(v) || d.slug.toLowerCase().includes(v);
      });
    });
  }
}

function closeSumModal() {
  document.getElementById('sum-backdrop').classList.remove('open');
  document.getElementById('sum-modal').classList.remove('open');
  document.body.style.overflow = '';
}

// ── tab switching ──────────────────────────────────────────────────────────
function switchTab(id, btn) {
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + id).classList.add('active');
  btn.classList.add('active');
  if (id === 'summary')  initSummary();
  if (id === 'pages')    initPages();
  if (id === 'posts')    initPosts();
  if (id === 'drafts')   initDrafts();
  if (id === 'classify') initClassify();
  if (id === 'triage')   initTriage();
}

// ── formatters ─────────────────────────────────────────────────────────────
function slugFmt(cell) {
  var d = cell.getData();
  return '<span class="t-link">/' + d.slug + '</span>';
}
function pathFmt(cell) {
  var d = cell.getData();
  return '<a class="t-link" href="' + d.url + '" target="_blank">' + d.path + '</a>';
}
function idFmt(cell)    { return '<span class="t-id">' + cell.getValue() + '</span>'; }
function titleFmt(cell) {
  var d = cell.getData();
  return '<span class="t-title">' + cell.getValue() + '</span>'
       + '<a class="t-ext-btn" href="' + d.url + '" target="_blank" title="Open in new tab" onclick="event.stopPropagation()">&#8599;</a>';
}
function dateFmt(v)     {
  return v ? '<span class="t-muted">' + v + '</span>'
           : '<span class="t-muted" style="opacity:.35">—</span>';
}
function statusFmt(cell) {
  var v = (cell.getValue() || '').toLowerCase();
  var cls = v === 'draft' ? 'badge-draft' : (v === 'private' ? 'badge-private' : 'badge-draft');
  return '<span class="badge ' + cls + '">' + v + '</span>';
}
function draftDateFmt(cell) {
  var v = cell.getValue();
  if (!v) return '<span class="t-muted" style="opacity:.35">—</span>';
  try {
    var d = new Date(v.replace(' ', 'T'));
    return '<span class="t-muted">' + d.toLocaleDateString('en-US',{year:'numeric',month:'short',day:'numeric'}) + '</span>';
  } catch(e) { return '<span class="t-muted">' + v + '</span>'; }
}

// ── shared Tabulator column config ─────────────────────────────────────────
function pagesCols() {
  return [
    { title:'ID',        field:'id',       width:68,  hozAlign:'center', sorter:'number', formatter:idFmt },
    { title:'Slug',      field:'slug',     widthGrow:2, formatter:slugFmt, sorter:'string' },
    { title:'Title',     field:'title',    widthGrow:3, formatter:titleFmt, sorter:'string' },
    { title:'Published', field:'pub_iso',  width:140, sorter:'date', sorterParams:{format:'YYYY-MM-DD'},
      formatter:function(c){ return dateFmt(c.getData().published); } },
    { title:'Modified',  field:'mod_iso',  width:140, sorter:'date', sorterParams:{format:'YYYY-MM-DD'},
      formatter:function(c){ return dateFmt(c.getData().modified); } },
  ];
}

// ── classification ─────────────────────────────────────────────────────────
var CAT_CFG = [
  { key:'Main Site',      color:'#405189', label:'Main Site' },
  { key:'Program / Event',color:'#0ab39c', label:'Program / Event' },
  { key:'Content',        color:'#299cdb', label:'Content' },
  { key:'System',         color:'#878a99', label:'System' },
  { key:'Thank You',      color:'#f7b84b', label:'Thank You' },
];

function catBadgeFmt(cell) {
  var v = cell.getValue();
  var cfg = CAT_CFG.find(function(c){ return c.key === v; }) || { color:'#878a99' };
  return '<span style="background:'+cfg.color+'22;color:'+cfg.color+';padding:.18rem .48rem;border-radius:4px;font-size:.68rem;font-weight:700;white-space:nowrap">'+v+'</span>';
}

function dupFmt(cell) {
  return cell.getValue()
    ? '<span style="background:#f0654820;color:#f06548;padding:.18rem .48rem;border-radius:4px;font-size:.68rem;font-weight:700">Possible dup</span>'
    : '';
}

var classifyTable = null;
var activeFilter  = '';

function initClassify() {
  if (classifyTable) {
    buildCcGrid();
    return;
  }

  // count by category
  var counts = {};
  var dupCount = 0;
  PAGES_DATA.forEach(function(d) {
    counts[d.category] = (counts[d.category] || 0) + 1;
    if (d.is_dup) dupCount++;
  });

  buildCcGrid(counts, dupCount);

  classifyTable = new Tabulator('#classify-table', {
    data: PAGES_DATA, layout: 'fitColumns', height: 480,
    initialSort: [{ column:'category', dir:'asc' }],
    columns: [
      { title:'Category',  field:'category', width:150, formatter:catBadgeFmt, sorter:'string' },
      { title:'Title',     field:'title',    widthGrow:3, formatter:titleFmt,  sorter:'string' },
      { title:'Slug',      field:'slug',     widthGrow:2, formatter:slugFmt,   sorter:'string' },
      { title:'Year',      field:'year',     width:72,  hozAlign:'center',
        formatter:function(c){ return '<span class="t-muted">'+c.getValue()+'</span>'; } },
      { title:'Duplicate?',field:'is_dup',   width:120, hozAlign:'center', formatter:dupFmt },
      { title:'Published', field:'pub_iso',  width:130, sorter:'date',
        sorterParams:{format:'YYYY-MM-DD'},
        formatter:function(c){ return dateFmt(c.getData().published); } },
    ],
  });
  classifyTable.on('rowClick', function(e, row) { var d = row.getData(); openRowPanel(d.url, d.title); });

  document.getElementById('classify-search').addEventListener('input', function() {
    var v = this.value.toLowerCase();
    applyClassifyFilter(v, activeFilter);
  });
}

function buildCcGrid(counts, dupCount) {
  // cards
  var grid = document.getElementById('cc-grid');
  if (grid.children.length) return;
  CAT_CFG.forEach(function(cfg) {
    var n = (counts && counts[cfg.key]) || 0;
    var el = document.createElement('div');
    el.className = 'cc'; el.style.setProperty('--cc-color', cfg.color);
    el.innerHTML = '<div class="cc-count">'+n+'</div><div class="cc-label">'+cfg.label+'</div>';
    el.onclick = function() { filterCat(cfg.key, el); };
    grid.appendChild(el);
  });
  // dup card
  var dup = document.createElement('div');
  dup.className = 'cc'; dup.style.setProperty('--cc-color', '#f06548');
  dup.innerHTML = '<div class="cc-count" style="color:#f06548">'+(dupCount||0)+'</div><div class="cc-label">Possible Dup</div>';
  dup.onclick = function() { filterDups(dup); };
  grid.appendChild(dup);

  // filter buttons
  var row = document.getElementById('cat-filter-row');
  var allBtn = document.createElement('button');
  allBtn.className = 'cat-filter-btn active'; allBtn.textContent = 'All';
  allBtn.style.background = '#405189';
  allBtn.onclick = function() { filterCat('', allBtn); };
  row.appendChild(allBtn);
  CAT_CFG.forEach(function(cfg) {
    var btn = document.createElement('button');
    btn.className = 'cat-filter-btn'; btn.textContent = cfg.label;
    btn.style.color = cfg.color;
    btn.onclick = function() { filterCat(cfg.key, btn); };
    row.appendChild(btn);
  });
  var dupBtn = document.createElement('button');
  dupBtn.className = 'cat-filter-btn'; dupBtn.textContent = 'Possible Dup';
  dupBtn.style.color = '#f06548';
  dupBtn.onclick = function() { filterDups(dupBtn); };
  row.appendChild(dupBtn);
}

function filterCat(cat, btn) {
  activeFilter = cat;
  document.querySelectorAll('.cat-filter-btn').forEach(function(b){ b.classList.remove('active'); b.style.background=''; });
  document.querySelectorAll('.cc').forEach(function(c){ c.classList.remove('active'); });
  if (btn) {
    btn.classList.add('active');
    var color = btn.style.color || '#405189';
    btn.style.background = color;
    btn.style.color = '#fff';
  }
  applyClassifyFilter(document.getElementById('classify-search').value.toLowerCase(), cat, false);
}

function filterDups(btn) {
  activeFilter = '__dup__';
  document.querySelectorAll('.cat-filter-btn').forEach(function(b){ b.classList.remove('active'); b.style.background=''; });
  if (btn) { btn.classList.add('active'); btn.style.background='#f06548'; btn.style.color='#fff'; }
  classifyTable.setFilter(function(d){ return d.is_dup; });
}

function applyClassifyFilter(search, cat, isDup) {
  if (!classifyTable) return;
  classifyTable.setFilter(function(d) {
    var matchCat = !cat || d.category === cat;
    var matchSearch = !search || d.title.toLowerCase().includes(search) || d.slug.toLowerCase().includes(search);
    return matchCat && matchSearch;
  });
}

// ── pages table ────────────────────────────────────────────────────────────
var pagesTable = null;
function initPages() {
  if (pagesTable) return;
  pagesTable = new Tabulator('#pages-table', {
    data: PAGES_DATA, layout: 'fitColumns', height: 520,
    columns: pagesCols(),
  });
  pagesTable.on('rowClick', function(e, row) { var d = row.getData(); openRowPanel(d.url, d.title); });
  document.getElementById('pages-search').addEventListener('input', function() {
    var v = this.value.toLowerCase();
    if (!v) { pagesTable.clearFilter(); return; }
    pagesTable.setFilter(function(d) {
      return d.title.toLowerCase().includes(v) || d.slug.toLowerCase().includes(v);
    });
  });
}

// ── drafts table ───────────────────────────────────────────────────────────
var draftsTable     = null;
var draftPostsTable = null;

function draftCols(extraCols) {
  var base = [
    { title:'Title',         field:'title',         widthGrow:4, formatter:titleFmt, sorter:'string' },
    { title:'Author',        field:'author',        width:160, sorter:'string',
      formatter:function(c){ return '<span class="t-muted">'+c.getValue()+'</span>'; } },
    { title:'Last Modified', field:'last_modified', width:155, sorter:'date',
      sorterParams:{format:'YYYY-MM-DD HH:mm'}, formatter:draftDateFmt },
    { title:'Status', field:'status', width:80, hozAlign:'center', formatter:statusFmt },
  ];
  return extraCols ? base.concat(extraCols) : base;
}

function initDrafts() {
  if (!draftsTable) {
    draftsTable = new Tabulator('#drafts-table', {
      data: DRAFTS_DATA, layout: 'fitColumns', height: 360,
      initialSort: [{ column:'last_modified', dir:'desc' }],
      columns: draftCols(),
    });
    document.getElementById('drafts-search').addEventListener('input', function() {
      var v = this.value.toLowerCase();
      if (!v) { draftsTable.clearFilter(); return; }
      draftsTable.setFilter(function(d) {
        return d.title.toLowerCase().includes(v) || (d.author||'').toLowerCase().includes(v);
      });
    });
  }
  if (!draftPostsTable) {
    draftPostsTable = new Tabulator('#draft-posts-table', {
      data: DRAFT_POSTS_DATA, layout: 'fitColumns', height: 320,
      initialSort: [{ column:'last_modified', dir:'desc' }],
      columns: draftCols([
        { title:'Categories', field:'categories', width:180, sorter:'string',
          formatter:function(c){ return '<span class="t-muted">'+c.getValue()+'</span>'; } },
      ]),
    });
    document.getElementById('draft-posts-search').addEventListener('input', function() {
      var v = this.value.toLowerCase();
      if (!v) { draftPostsTable.clearFilter(); return; }
      draftPostsTable.setFilter(function(d) {
        return d.title.toLowerCase().includes(v) || (d.author||'').toLowerCase().includes(v);
      });
    });
  }
}

// ── posts table ────────────────────────────────────────────────────────────
var postsTable = null;
function initPosts() {
  if (postsTable) return;
  postsTable = new Tabulator('#posts-table', {
    data: POSTS_DATA, layout: 'fitColumns', height: 520,
    initialSort: [{ column:'pub_iso', dir:'desc' }],
    columns: pagesCols(),
  });
  postsTable.on('rowClick', function(e, row) { var d = row.getData(); openRowPanel(d.url, d.title); });
  document.getElementById('posts-search').addEventListener('input', function() {
    var v = this.value.toLowerCase();
    if (!v) { postsTable.clearFilter(); return; }
    postsTable.setFilter(function(d) {
      return d.title.toLowerCase().includes(v) || d.slug.toLowerCase().includes(v);
    });
  });
}

// ── triage table ───────────────────────────────────────────────────────────
var triageTable = null;
var triageFilter = '';

var TRIAGE_BUCKETS = [
  { key:'KEEP',   label:'Keep — migrate',   sub:'Evergreen series + clean content', color:'#0ab39c' },
  { key:'DROP',   label:'Drop — skip',      sub:'WP team pre-tagged as Exclude',    color:'#f06548' },
  { key:'REVIEW', label:'Manual review',    sub:'Heuristics need a second look',    color:'#c9950a' },
];

function verdictBadgeFmt(cell) {
  var v = (cell.getValue() || '').toUpperCase();
  var cls = v === 'KEEP' ? 'verdict-keep' : (v === 'DROP' ? 'verdict-drop' : 'verdict-review');
  return '<span class="verdict-badge ' + cls + '">' + v + '</span>';
}

function flagsFmt(cell) {
  var flags = cell.getValue() || [];
  if (!flags.length) return '<span class="t-muted" style="opacity:.4">—</span>';
  return flags.slice(0, 4).map(function(f) {
    var cls = 'flag-chip';
    if (/missing|gaps|short/.test(f)) cls += ' warn';
    return '<span class="'+cls+'">' + f + '</span>';
  }).join('');
}

function wordsFmt(cell) {
  var v = cell.getValue() || 0;
  var color = v < 200 ? '#f06548' : (v < 400 ? '#c9950a' : 'var(--muted)');
  return '<span class="t-muted" style="color:'+color+'">' + v + '</span>';
}

function initTriage() {
  if (triageTable) return;

  var counts = { KEEP: 0, DROP: 0, REVIEW: 0 };
  TRIAGE_DATA.forEach(function(d) {
    counts[d.verdict] = (counts[d.verdict] || 0) + 1;
  });

  // build verdict cards
  var grid = document.getElementById('tri-grid');
  TRIAGE_BUCKETS.forEach(function(cfg) {
    var n = counts[cfg.key] || 0;
    var el = document.createElement('div');
    el.className = 'tri-card';
    el.style.setProperty('--cc-color', cfg.color);
    el.innerHTML =
      '<div class="tri-count">' + n + '</div>' +
      '<div class="tri-label">' + cfg.label + '</div>' +
      '<div class="tri-sub">' + cfg.sub + '</div>';
    el.onclick = function() { filterTriage(cfg.key, el); };
    grid.appendChild(el);
  });

  // chip filters
  var row = document.getElementById('tri-filter-row');
  var allBtn = document.createElement('button');
  allBtn.className = 'cat-filter-btn active';
  allBtn.textContent = 'All (' + TRIAGE_DATA.length + ')';
  allBtn.style.background = '#405189';
  allBtn.onclick = function() { filterTriage('', allBtn); };
  row.appendChild(allBtn);
  TRIAGE_BUCKETS.forEach(function(cfg) {
    var btn = document.createElement('button');
    btn.className = 'cat-filter-btn';
    btn.textContent = cfg.key + ' (' + (counts[cfg.key] || 0) + ')';
    btn.style.color = cfg.color;
    btn.dataset.color = cfg.color;
    btn.onclick = function() { filterTriage(cfg.key, btn); };
    row.appendChild(btn);
  });

  triageTable = new Tabulator('#triage-table', {
    data: TRIAGE_DATA, layout: 'fitColumns', height: 540,
    initialSort: [{ column:'verdict', dir:'asc' }, { column:'pub_iso', dir:'desc' }],
    columns: [
      { title:'Verdict', field:'verdict', width:96, hozAlign:'center', sorter:'string', formatter:verdictBadgeFmt },
      { title:'Title',   field:'title', widthGrow:3, formatter:titleFmt, sorter:'string' },
      { title:'Slug',    field:'slug',  widthGrow:2, formatter:slugFmt,  sorter:'string' },
      { title:'Category',field:'cat_primary', width:160, sorter:'string',
        formatter:function(c){ return '<span class="t-muted">'+(c.getValue()||'—')+'</span>'; } },
      { title:'Published',field:'pub_iso', width:120, sorter:'date', sorterParams:{format:'YYYY-MM-DD'},
        formatter:function(c){ return dateFmt(c.getData().published); } },
      { title:'Words',   field:'words', width:74, hozAlign:'right', sorter:'number', formatter:wordsFmt },
      { title:'SEO/Quality flags', field:'flags', widthGrow:2, sorter:false, formatter:flagsFmt },
    ],
  });

  triageTable.on('rowClick', function(e, row) {
    var d = row.getData();
    openRowPanel(d.url, d.title);
  });

  document.getElementById('triage-search').addEventListener('input', function() {
    applyTriageFilter(this.value.toLowerCase(), triageFilter);
  });
}

function filterTriage(verdict, btn) {
  triageFilter = verdict;
  document.querySelectorAll('#tri-filter-row .cat-filter-btn').forEach(function(b){
    b.classList.remove('active'); b.style.background = '';
  });
  btn.classList.add('active');
  if (verdict) {
    var color = btn.dataset.color || '#405189';
    btn.style.background = color;
    btn.style.color = '#fff';
  } else {
    btn.style.background = '#405189';
    btn.style.color = '#fff';
  }
  var search = document.getElementById('triage-search').value.toLowerCase();
  applyTriageFilter(search, verdict);
}

function applyTriageFilter(search, verdict) {
  if (!triageTable) return;
  triageTable.setFilter(function(d) {
    if (verdict && d.verdict !== verdict) return false;
    if (!search) return true;
    return d.title.toLowerCase().includes(search) || d.slug.toLowerCase().includes(search);
  });
}

// ── sitemap panel (single Tabulator, data replaced per tile) ───────────────
var smTable  = null;
var smActive = null;

function openSitemap(name, el) {
  if (smActive === name) { closeSitemap(); return; }
  smActive = name;
  document.querySelectorAll('.sm-tile').forEach(t => t.classList.remove('active'));
  el.classList.add('active');

  var d = SITEMAP_DATA[name];
  document.getElementById('sph-label').textContent = d.label;
  document.getElementById('sph-desc').textContent  = d.desc;
  document.getElementById('sph-count').textContent  = d.count + ' URLs';
  document.getElementById('sph-xml').href           = d.src;
  document.getElementById('sm-search').value = '';

  var panel = document.getElementById('sm-panel');
  panel.classList.add('open');

  if (smTable) {
    smTable.replaceData(d.urls);
  } else {
    smTable = new Tabulator('#sm-table', {
      data: d.urls, layout: 'fitColumns', height: 360,
      columns: [
        { title:'#', field:'_i', width:50, hozAlign:'center', sorter:false,
          formatter:function(c){ return '<span class="t-id">'+(c.getRow().getPosition(true)+1)+'</span>'; } },
        { title:'Path / URL', field:'path', widthGrow:3, formatter:pathFmt, sorter:'string' },
        { title:'Last Modified', field:'lastmod', width:155,
          formatter:function(c){ return dateFmt(c.getValue()); },
          sorter:'date', sorterParams:{format:'YYYY-MM-DD'} },
      ]
    });
    smTable.on('rowClick', function(e, row) { window.open(row.getData().url, '_blank'); });
    document.getElementById('sm-search').addEventListener('input', function() {
      var v = this.value.toLowerCase();
      if (!v) { smTable.clearFilter(); return; }
      smTable.setFilter(function(d) { return (d.path||'').toLowerCase().includes(v); });
    });
  }

  setTimeout(function() {
    panel.scrollIntoView({ behavior:'smooth', block:'nearest' });
  }, 60);
}

function closeSitemap() {
  smActive = null;
  document.querySelectorAll('.sm-tile').forEach(t => t.classList.remove('active'));
  document.getElementById('sm-panel').classList.remove('open');
}

// ── iframe preview ─────────────────────────────────────────────────────────
var currentUrl = '__FIRST_NAV__';

function loadPreview(url, card) {
  document.querySelectorAll('.nc').forEach(c => c.classList.remove('active'));
  card.classList.add('active');
  currentUrl = url;
  document.getElementById('chrome-url').textContent = url;
  document.getElementById('chrome-open').href = url;
  document.getElementById('blocked-link').href = url;
  document.getElementById('blocked-msg').classList.remove('show');

  // show loader
  var loader = document.getElementById('iframe-loader');
  loader.classList.remove('done');
  var frame = document.getElementById('preview-frame');
  frame.style.opacity = '0';
  frame.src = url;
}

function onFrameLoad(frame) {
  document.getElementById('iframe-loader').classList.add('done');
  frame.style.opacity = '1';
  try {
    var doc = frame.contentDocument || frame.contentWindow.document;
    if (!doc || !doc.body || doc.body.innerHTML.trim() === '') showBlocked();
  } catch(e) {
    frame.style.opacity = '1';
    document.getElementById('iframe-loader').classList.add('done');
  }
}

function showBlocked() {
  document.getElementById('iframe-loader').classList.add('done');
  document.getElementById('preview-frame').style.opacity = '0';
  document.getElementById('blocked-msg').classList.add('show');
  document.getElementById('blocked-link').href = currentUrl;
}

// ── row preview panel (Active Pages & Blog Posts) ──────────────────────────
var rpUrl = '';
var rpCloseTimer = null;

function openRowPanel(url, title) {
  rpUrl = url;
  if (rpCloseTimer) { clearTimeout(rpCloseTimer); rpCloseTimer = null; }

  document.getElementById('rp-title').textContent = title;
  document.getElementById('rp-url').textContent   = url;
  document.getElementById('rp-ext').href          = url;
  document.getElementById('rp-blocked-link').href = url;
  document.getElementById('rp-blocked').classList.remove('show');

  var loader = document.getElementById('rp-loader');
  loader.classList.remove('done');
  var frame = document.getElementById('rp-frame');
  frame.style.opacity = '0';
  frame.src = url;

  document.getElementById('row-panel').classList.add('open');
  document.getElementById('rp-backdrop').classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeRowPanel() {
  document.getElementById('row-panel').classList.remove('open');
  document.getElementById('rp-backdrop').classList.remove('open');
  document.body.style.overflow = '';
  rpCloseTimer = setTimeout(function() {
    document.getElementById('rp-frame').src = 'about:blank';
  }, 340);
}

function onRpLoad(frame) {
  document.getElementById('rp-loader').classList.add('done');
  frame.style.opacity = '1';
  try {
    var doc = frame.contentDocument || frame.contentWindow.document;
    if (!doc || !doc.body || doc.body.innerHTML.trim() === '') showRpBlocked();
  } catch(e) {
    frame.style.opacity = '1';
  }
}

function showRpBlocked() {
  document.getElementById('rp-loader').classList.add('done');
  document.getElementById('rp-frame').style.opacity = '0';
  document.getElementById('rp-blocked').classList.add('show');
  document.getElementById('rp-blocked-link').href = rpUrl;
}

document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') { closeSumModal(); closeRowPanel(); }
});

// init default tab on load
initSummary();

// wire rp-frame events here so onRpLoad / showRpBlocked are already defined
(function() {
  var f = document.getElementById('rp-frame');
  f.addEventListener('load', function() {
    if (this.src === 'about:blank') return;
    onRpLoad(this);
  });
  f.addEventListener('error', showRpBlocked);
})();
</script>
</body>
</html>"""

# ── generate ──────────────────────────────────────────────────────────────────

def generate_html(today, n_pages, n_posts, n_drafts, n_nav, total_sm,
                  nav, sm, pages_json, posts_json, sm_json, drafts_json,
                  draft_posts_json, triage_json, triage_counts, first_nav):
    nav_cards_html = render_nav_cards(nav)
    sm_tiles_html  = render_sitemap_tiles(sm)

    n_total  = n_pages + n_posts
    top      = max(n_pages, n_posts, n_drafts, n_nav)
    pct      = lambda n: str(round(n / top * 100)) if top else "0"

    n_triage = triage_counts.get("total", 0)
    n_keep   = triage_counts.get("keep", 0)
    n_drop   = triage_counts.get("drop", 0)

    return (HTML_TEMPLATE
        .replace("__TODAY__",         today)
        .replace("__BASE_URL__",      BASE_URL)
        .replace("__BASE_URL_CLEAN__",BASE_URL.replace("https://",""))
        .replace("__N_PAGES__",       str(n_pages))
        .replace("__N_POSTS__",       str(n_posts))
        .replace("__N_DRAFTS__",      str(n_drafts))
        .replace("__N_NAV__",         str(n_nav))
        .replace("__N_TOTAL__",       str(n_total))
        .replace("__PCT_PAGES__",     pct(n_pages))
        .replace("__PCT_POSTS__",     pct(n_posts))
        .replace("__PCT_DRAFTS__",    pct(n_drafts))
        .replace("__PCT_NAV__",       pct(n_nav))
        .replace("__TOTAL_SM__",      str(total_sm))
        .replace("__N_TRIAGE__",      str(n_triage))
        .replace("__N_TRIAGE_KEEP__", str(n_keep))
        .replace("__N_TRIAGE_DROP__", str(n_drop))
        .replace("__FIRST_NAV__",     first_nav)
        .replace("__PAGES_JSON__",    pages_json)
        .replace("__POSTS_JSON__",    posts_json)
        .replace("__SM_JSON__",       sm_json)
        .replace("__DRAFTS_JSON__",      drafts_json)
        .replace("__DRAFT_POSTS_JSON__", draft_posts_json)
        .replace("__TRIAGE_JSON__",      triage_json)
        .replace("__N_DRAFT_POSTS__",    str(len(DRAFT_POSTS)))
        .replace("__NAV_CARDS_HTML__",   nav_cards_html)
        .replace("__SM_TILES_HTML__", sm_tiles_html)
    )

# ── main ──────────────────────────────────────────────────────────────────────

VERDICT_LABEL_MAP = {
    "auto_drop": "DROP",
    "auto_keep": "KEEP",
    "auto_flag_review": "REVIEW",
    "neutral": "KEEP",
}


def load_triage_data():
    """Load extract_blog_data.py output if present, return (rows, counts) for HTML.

    rows is the compact JSON-ready list the Tabulator triage table consumes;
    counts is a small dict with total/keep/drop for KPI binding. If the
    sidecar file is missing, returns empty data so the tab degrades gracefully.
    """
    sidecar = os.path.join(OUT_DIR, "data", "posts_extracted.json")
    if not os.path.isfile(sidecar):
        print(f"  → no triage data found at {sidecar} (run extract_blog_data.py first)")
        return [], {"total": 0, "keep": 0, "drop": 0, "review": 0}

    try:
        with open(sidecar, "r", encoding="utf-8") as fh:
            payload = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"  → failed to load triage data: {exc}")
        return [], {"total": 0, "keep": 0, "drop": 0, "review": 0}

    posts = payload.get("posts", [])
    rows = []
    counts = {"total": 0, "keep": 0, "drop": 0, "review": 0}
    for p in posts:
        verdict = VERDICT_LABEL_MAP.get(p.get("auto_verdict", ""), "REVIEW")
        rows.append({
            "id": p.get("id"),
            "slug": p.get("slug", ""),
            "url": p.get("url", ""),
            "title": p.get("title", ""),
            "verdict": verdict,
            "categories": p.get("categories", []),
            "cat_primary": (p.get("categories") or ["—"])[0],
            "published": fmt_date(p.get("published_iso", "")),
            "pub_iso": (p.get("published_iso", "") or "")[:10],
            "modified": fmt_date(p.get("modified_iso", "")),
            "mod_iso": (p.get("modified_iso", "") or "")[:10],
            "words": p.get("word_count", 0),
            "images": p.get("image_count", 0),
            "images_no_alt": p.get("images_missing_alt", 0),
            "internal_links": p.get("internal_link_count", 0),
            "yoast_title": p.get("yoast_title", ""),
            "yoast_description": p.get("yoast_description", ""),
            "flags": p.get("quality_flags", []),
            "reasons": p.get("auto_reasons", []),
        })
        counts["total"] += 1
        if verdict == "DROP":
            counts["drop"] += 1
        elif verdict == "REVIEW":
            counts["review"] += 1
        else:
            counts["keep"] += 1
    rows.sort(key=lambda r: (r["verdict"] != "DROP", r["pub_iso"]), reverse=True)
    return rows, counts


def run():
    today = datetime.now().strftime("%B %d, %Y")

    print("Fetching pages…")
    pages_raw = [p for p in fetch_all_paginated(f"{WP_API}/pages") if p.get("status") == "publish"]
    print(f"  → {len(pages_raw)} pages")

    print("Fetching posts…")
    posts_raw = [p for p in fetch_all_paginated(f"{WP_API}/posts") if p.get("status") == "publish"]
    print(f"  → {len(posts_raw)} posts")

    print("Scanning sitemaps…")
    sm = get_sitemaps()
    total_sm = sum(d["count"] for d in sm.values())
    print(f"  → {len(sm)} sitemaps, {total_sm} URLs")

    print("Parsing navigation…")
    nav = get_nav()
    print(f"  → {len(nav)} nav links")

    print("Loading blog migration triage…")
    triage_rows, triage_counts = load_triage_data()
    print(f"  → {triage_counts['total']} triage rows (keep={triage_counts['keep']}, drop={triage_counts['drop']})")

    pages_json       = json.dumps(build_page_data(pages_raw), ensure_ascii=False)
    posts_json       = json.dumps(build_post_data(posts_raw), ensure_ascii=False)
    drafts_json      = json.dumps(DRAFT_PAGES,                ensure_ascii=False)
    draft_posts_json = json.dumps(DRAFT_POSTS,                ensure_ascii=False)
    triage_json      = json.dumps(triage_rows,                ensure_ascii=False)

    sm_payload = {
        name: {"label": d["label"], "desc": d["desc"],
               "count": d["count"], "src": d["src"], "urls": d["urls"]}
        for name, d in sm.items()
    }
    sm_json    = json.dumps(sm_payload, ensure_ascii=False)
    first_nav  = nav[0] if nav else BASE_URL

    html = generate_html(today, len(pages_raw), len(posts_raw), len(DRAFT_PAGES),
                         len(nav), total_sm, nav, sm,
                         pages_json, posts_json, sm_json, drafts_json,
                         draft_posts_json, triage_json, triage_counts, first_nav)

    with open(HTML_OUT, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\nReport → {HTML_OUT}")
    print(f"  Pages: {len(pages_raw)}  Posts: {len(posts_raw)}  Drafts: {len(DRAFT_PAGES)}")
    print(f"  Nav: {len(nav)}  Sitemap URLs: {total_sm}")
    print(f"  Triage: {triage_counts['total']} (keep={triage_counts['keep']}, drop={triage_counts['drop']})")


if __name__ == "__main__":
    run()
