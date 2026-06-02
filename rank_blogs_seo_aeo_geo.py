#!/usr/bin/env python3
"""
rank_blogs_seo_aeo_geo.py — Rankea los 167 keeps y saca el TOP 50.

Rubrica determinista (0-100), 3 ejes (sin gastar API por post):
  SEO  (40) — descubribilidad en buscadores:
       title 30-65 (8) · profundidad palabras (12) · estructura h2/h3 (8)
       · internal links (6) · keyword/topic claro en title (6)
  AEO  (30) — Answer Engine (snippets, voz, AI Overviews):
       title = pregunta/how-to (10) · listas/"What You'll Discover" (10)
       · capitulado con timestamps (10)
  GEO  (30) — Generative Engine (citabilidad por LLMs):
       profundidad+secciones (10) · entidades nombradas/autoridad (10)
       · evergreen + perspectiva unica/framework (10)

Entradas:  data/posts_extracted.json + data/wp_cache/{id}.json (cuerpos)
Salidas:   data/blog_ranking.json  (167 rankeados, con sub-scores + razones)
           SOTSI_Blog_Top50_SEO_AEO_GEO.csv
"""
import json, os, re, html
from html.parser import HTMLParser

BASE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(BASE, "data", "wp_cache")
SRC = os.path.join(BASE, "data", "posts_extracted.json")
OUT_JSON = os.path.join(BASE, "data", "blog_ranking.json")
OUT_CSV = os.path.join(BASE, "SOTSI_Blog_Top50_SEO_AEO_GEO.csv")

PILOT = {21752: "soul-feast-82", 21765: "soul-snack-83", 21600: "soul-feast-73"}

# Entidades de autoridad (señal GEO: nombres propios citables)
AUTHORITY = ["Oprah", "Maya Angelou", "Scarlett Lewis", "Paulo Coelho",
             "Gwyneth Paltrow", "Lewis Howes", "Jay-Z", "Julianne Hough",
             "Krishna", "Buddha", "Jesus", "Christ", "Gandhi", "Martin Luther King",
             "Bhagavad Gita", "Mahabharata", "Sandy Hook", "Choose Love",
             "Dancing Wu Li", "Seat of the Soul", "Genesis", "Arjuna"]

QUESTION_RE = re.compile(r"\?|^\s*(how|why|what|when|where|who|can|should|is|are|do|does)\b", re.I)
TS_RE = re.compile(r"\(\d{1,2}:\d{2}\)")


class Body(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.text = []
        self.h = 0
        self.li = 0

    def handle_starttag(self, t, a):
        if t in ("h2", "h3", "h4"):
            self.h += 1
        if t == "li":
            self.li += 1

    def handle_data(self, d):
        self.text.append(d)

    def parsed(self):
        return "".join(self.text), self.h, self.li


def body_signals(pid):
    fp = os.path.join(CACHE, f"{pid}.json")
    if not os.path.exists(fp):
        return None
    j = json.load(open(fp, encoding="utf-8"))
    raw = j.get("content", {}).get("rendered", "")
    b = Body()
    b.feed(raw)
    text, nh, nli = b.parsed()
    text = re.sub(r"\s+", " ", text)
    words = len(text.split())
    has_video = bool(re.search(r"youtube|vimeo", raw))
    timestamps = len(TS_RE.findall(text))
    entities = sorted({e for e in AUTHORITY if e.lower() in text.lower()})
    return {"words": words, "h": nh, "li": nli, "video": has_video,
            "timestamps": timestamps, "entities": entities,
            "excerpt": html.unescape(re.sub("<[^>]+>", "", j.get("excerpt", {}).get("rendered", "")))[:200]}


def score_seo(title, sig, p):
    s, why = 0, []
    tl = len(title)
    if 30 <= tl <= 65:
        s += 8; why.append("title len ok")
    elif tl <= 75:
        s += 5
    else:
        s += 2; why.append("title largo")
    w = sig["words"]
    s += 12 if w >= 800 else 9 if w >= 600 else 6 if w >= 400 else 3
    if w < 400:
        why.append("contenido corto")
    s += 8 if sig["h"] >= 3 else 5 if sig["h"] >= 1 else 0
    il = p.get("internal_link_count", 0)
    s += 6 if il >= 3 else 4 if il >= 1 else 0
    # topic claro: serie + tema en title
    if ":" in title or "–" in title or "?" in title:
        s += 6
    else:
        s += 3
    return s, why


def score_aeo(title, sig):
    s, why = 0, []
    if QUESTION_RE.search(title):
        s += 10; why.append("title pregunta/how-to")
    else:
        s += 3
    if sig["li"] >= 4:
        s += 10; why.append("listas ricas")
    elif sig["li"] >= 1:
        s += 6
    if sig["timestamps"] >= 4:
        s += 10; why.append("capitulado (timestamps)")
    elif sig["timestamps"] >= 1:
        s += 6
    return s, why


def score_geo(title, sig):
    s, why = 0, []
    w, sec = sig["words"], sig["h"] + sig["li"]
    s += 10 if (w >= 700 and sec >= 5) else 7 if (w >= 500 and sec >= 3) else 4
    ne = len(sig["entities"])
    s += 10 if ne >= 3 else 7 if ne == 2 else 5 if ne == 1 else 2
    if ne >= 2:
        why.append("entidades: " + ", ".join(sig["entities"][:4]))
    # perspectiva unica: Soul Feast = deep-dive original > Soul Snack
    tl = title.lower()
    if "feast" in tl:
        s += 10; why.append("deep-dive (Feast)")
    elif "snack" in tl:
        s += 7
    else:
        s += 6
    return s, why


def main():
    posts = json.load(open(SRC, encoding="utf-8"))["posts"]
    keeps = [p for p in posts if p.get("auto_verdict") == "auto_keep"]
    ranked, skipped = [], 0
    for p in keeps:
        pid = int(p["id"])
        sig = body_signals(pid)
        if not sig:
            skipped += 1
            continue
        title = html.unescape(p.get("title", ""))
        seo, w1 = score_seo(title, sig, p)
        aeo, w2 = score_aeo(title, sig)
        geo, w3 = score_geo(title, sig)
        total = seo + aeo + geo
        ranked.append({
            "id": pid, "title": title, "slug": p["slug"],
            "series": "Soul Feast" if "feast" in title.lower() else "Soul Snack" if "snack" in title.lower() else "Other",
            "words": sig["words"], "entities": sig["entities"],
            "seo": seo, "aeo": aeo, "geo": geo, "total": total,
            "already_migrated": pid in PILOT,
            "reasons": w1 + w2 + w3,
            "url": p.get("url", ""),
        })
    ranked.sort(key=lambda r: (-r["total"], -r["geo"], -r["words"]))
    for i, r in enumerate(ranked, 1):
        r["rank"] = i
        r["top50"] = i <= 50

    json.dump(ranked, open(OUT_JSON, "w"), ensure_ascii=False, indent=1)

    import csv
    with open(OUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["Rank", "Total", "SEO", "AEO", "GEO", "Series", "Words",
                    "Title", "Slug", "Entities", "Why", "AlreadyInDEV", "URL"])
        for r in ranked[:50]:
            w.writerow([r["rank"], r["total"], r["seo"], r["aeo"], r["geo"],
                        r["series"], r["words"], r["title"], r["slug"],
                        "; ".join(r["entities"]), " | ".join(r["reasons"]),
                        "yes" if r["already_migrated"] else "", r["url"]])

    top = ranked[:50]
    print(f"rankeados: {len(ranked)} (sin cuerpo: {skipped})")
    print(f"TOP50 — promedio total: {sum(r['total'] for r in top)/len(top):.1f}")
    from collections import Counter
    print("TOP50 series:", dict(Counter(r['series'] for r in top)))
    print("TOP50 ya en DEV:", sum(1 for r in top if r['already_migrated']))
    print("\n=== TOP 20 ===")
    for r in top[:20]:
        print(f"  #{r['rank']:>2} {r['total']:>3} (S{r['seo']}/A{r['aeo']}/G{r['geo']}) {r['title'][:58]}")
    print(f"\nCSV -> {OUT_CSV}\nJSON -> {OUT_JSON}")


if __name__ == "__main__":
    main()
