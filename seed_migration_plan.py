#!/usr/bin/env python3
"""Seed data/migration_plan.json from data/site_inventory.json.

Encodes the migration verdicts, archetypes, sprint assignments and per-role
hour benchmarks produced in the planning session (architect framework).
Re-runnable: regenerates the plan from the inventory + the overrides below.
Stdlib only. No pip, no API key.

Verdicts:  keep | improve | rebuild | consolidate | drop
Status:    backlog | design | content | build | review | done | blocked
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INV  = ROOT / "data" / "site_inventory.json"
OUT  = ROOT / "data" / "migration_plan.json"

# ── role-hour benchmarks per archetype (typical case) ──────────────────────────
# order: design, content, media, build, review
ARCHETYPE_HOURS = {
    "global":      (10, 2, 2, 12, 3),   # nav/footer/tokens/style guide (one-time)
    "hub":         (12, 6, 8, 12, 4),   # home
    "index":       (5,  3, 3, 5,  2),   # events index, get-started, media
    "program":     (6,  5, 4, 6,  2),   # program/landing pages
    "bio":         (5,  6, 5, 5,  2),   # founder/memorial bios
    "funnel":      (3,  3, 2, 3,  1),   # optin + TY pair (counted on the optin)
    "content":     (2,  3, 2, 2,  1),   # evergreen essay/teaching
    "consolidate": (5,  6, 4, 5,  2),   # merge N sources -> 1 survivor
    "template":    (2,  1, 1, 3,  1),   # generic reusable confirmation
    "legal":       (1,  1, 0, 2,  1),   # privacy/terms/refund/opt-out
    "commerce":    (8,  4, 4, 16, 3),   # shop / membership (RISK, spike)
    "redirect":    (0,  0, 0, 0,  0),   # drop / consolidate-loser: 301 only
}

# Pages that belong to UHF or shared/both. Everything else defaults to SOTSI.
UHF = {"universalhuman", "universal-human-audiobook-excerpt-chapter-28",
       "universal-human-celebrates-one-year", "ai-and-human-evolution"}
BOTH = {"home", "blog", "blog-2", "faqs", "connect", "media", "podcast",
        "privacy-policy", "terms-of-use", "refund-cancellation", "opt-out",
        "registration-received", "free-tools", "cart", "checkout", "my-account",
        "your-profile", "soul2soulcommunity", "subscribe-to-podcast"}

# ── per-slug overrides: (verdict, archetype, phase, sprint, [consolidate_into], [note]) ──
# Anything not listed defaults to: verdict=improve, archetype=content, phase=2, sprint=0.
O = {
    # ---- Main Site (22) ----
    "home": ("rebuild", "hub", 1, 1, None, "Hub de marca; ancla IA y componentes globales."),
    "about": ("rebuild", "program", 1, 2, None, "Pagina core, vieja (2021), rehacer en marca 2026."),
    "about-gary-zukav": ("rebuild", "bio", 1, 2, None, "Fundador, critica de marca."),
    "about-linda-francis": ("rebuild", "bio", 1, 2, None, "Co-fundadora; liga al tributo memorial."),
    "seat-of-the-soul-institute": ("consolidate", "consolidate", 1, 2, "about", "Solapa con about/home; fundir en About."),
    "books": ("rebuild", "program", 1, 3, None, "Ancla comercial; foto real + links de compra."),
    "get-started": ("rebuild", "index", 1, 3, None, "Pagina de orientacion/conversion primaria."),
    "events-and-programs": ("rebuild", "index", 1, 3, None, "Hub indice de programas; secuencia las demas."),
    "courses-lighten": ("rebuild", "program", 1, 3, None, "Curso activo (2025); rediseno en marca."),
    "podcast": ("improve", "content", 1, 4, None, "Activo (2025-11); refresh marca + SEO."),
    "media": ("improve", "index", 1, 4, None, "Pagina de prensa; refrescar assets."),
    "faqs": ("improve", "content", 1, 4, None, "FAQ actual; migrar + marca + SEO."),
    "connect": ("improve", "content", 1, 4, None, "Contacto; rehacer form en Webflow."),
    "soul-connections-newsletter": ("improve", "content", 1, 4, None, "Mas reciente (2026-02); signup + form."),
    "soul-connections-newsletter-archive": ("consolidate", "consolidate", 1, 4, "soul-connections-newsletter", "Fundir en newsletter; viejo (2021)."),
    "blog": ("consolidate", "index", 1, 5, None, "Indice canonico del blog; fusiona con blog-2."),
    "blog-2": ("drop", "redirect", 1, 5, "blog", "Duplicado de blog (2024); 301 al indice."),
    "ai-and-human-evolution": ("improve", "content", 1, 4, None, "Contenido UHF (2024) relevante; marca + SEO."),
    "failing-government": ("improve", "content", 1, 4, None, "Ensayo (2024); marca + SEO, confirmar mensaje."),
    "journey-to-the-soul-retreat-faqs": ("consolidate", "consolidate", 1, 3, "events-and-programs", "Fundir en FAQ del programa Journey."),
    "remember-linda-homepage": ("consolidate", "consolidate", 1, 2, None, "Hub del cluster memorial Linda; survivor del tributo."),
    "shop": ("rebuild", "commerce", 1, 5, None, "RIESGO: e-commerce; decidir plataforma (ver riesgos)."),

    # ---- Content (21) ----
    "free-tools": ("rebuild", "index", 1, 4, None, "Hub de herramientas; rediseno + marca."),
    "heartofthesoul": ("improve", "content", 1, 4, None, "Contenido evergreen; marca + SEO."),
    "universalhuman": ("improve", "content", 1, 4, None, "Contenido de marca UHF (purple/humanos)."),
    "multi-sensory-vocabulary": ("improve", "content", 1, 4, None, "Referencia evergreen; marca + SEO."),
    "questions-and-answers": ("improve", "content", 1, 4, None, "Q&A evergreen; marca + SEO."),
    "love-fear": ("improve", "funnel", 1, 4, None, "Teaching reciente (2025); par con love-fear-ty."),
    "responsible-choice": ("improve", "funnel", 1, 4, None, "Teaching reciente (2025); par con responsible-choice-ty."),
    "addiction": ("improve", "funnel", 1, 4, None, "Topic (2024); unidad con addiction-thank-you."),
    "judgment": ("improve", "funnel", 1, 4, None, "Topic (2024); unidad con judgement-thank-you (arreglar slug)."),
    "paulo-coelhos": ("improve", "content", 1, 4, None, "Tributo/ensayo evergreen; marca + SEO."),
    "subscribe-to-podcast": ("consolidate", "consolidate", 1, 4, "podcast", "Fundir en podcast; intento duplicado."),
    "gifts-of-the-pandemic": ("drop", "redirect", 1, 5, None, "Contenido de momento pandemia (2021)."),
    "share-your-favorite-quotes-the-seat-of-the-soul": ("drop", "redirect", 1, 5, None, "Campana UGC unica (2022) expirada."),
    "for-linda": ("consolidate", "consolidate", 1, 2, "remember-linda-homepage", "Cluster memorial Linda -> tributo unico."),
    "messages-for-linda": ("consolidate", "consolidate", 1, 2, "remember-linda-homepage", "Cluster memorial Linda."),
    "lindas-mailbox": ("consolidate", "consolidate", 1, 2, "remember-linda-homepage", "Cluster memorial Linda."),
    "linda-celebration": ("consolidate", "consolidate", 1, 2, "remember-linda-homepage", "Cluster memorial Linda."),
    "linda-francis-celebration-series": ("consolidate", "consolidate", 1, 2, "remember-linda-homepage", "Cluster memorial Linda."),
    "linda-francis-celebration-series-messages": ("consolidate", "consolidate", 1, 2, "remember-linda-homepage", "Cluster memorial Linda."),
    "happy-birthday-gary": ("drop", "redirect", 1, 5, None, "Saludo dated unico (2022)."),
    "wishes-for-gary": ("drop", "redirect", 1, 5, None, "Saludo dated unico (2022)."),

    # ---- Thank You (11) ----
    "love-fear-ty": ("improve", "funnel", 1, 4, "love-fear", "Par de love-fear."),
    "responsible-choice-ty": ("improve", "funnel", 1, 4, "responsible-choice", "Par de responsible-choice."),
    "addiction-thank-you": ("improve", "funnel", 1, 4, "addiction", "Par de addiction."),
    "judgement-thank-you": ("improve", "funnel", 1, 4, "judgment", "Par de judgment (arreglar spelling de slug)."),
    "apg-ty": ("improve", "funnel", 1, 4, "apg-optin", "Par de apg-optin."),
    "daily-intuition-ty": ("improve", "funnel", 1, 4, "daily-intuition-practice", "Par de daily-intuition-practice."),
    "multi-five-ty": ("improve", "funnel", 1, 4, "mutli-five-sensory", "Par de multisensory."),
    "soul-connections-newsletter-ty": ("improve", "funnel", 1, 4, "soul-connections-newsletter", "Par de newsletter."),
    "registration-received": ("consolidate", "template", 1, 1, None, "TY generico reusable; otros redirigen aqui."),
    "linda-celebration-thank-you": ("drop", "redirect", 1, 5, "remember-linda-homepage", "Cluster Linda consolidado/dropeado."),
    "message-to-linda-received": ("drop", "redirect", 1, 5, "remember-linda-homepage", "Cluster Linda."),

    # ---- Program / Event (43) ----
    "apg-optin": ("improve", "funnel", 1, 4, None, "Lead magnet activo (2025); unidad con apg-ty."),
    "daily-intuition-practice": ("improve", "funnel", 1, 4, None, "Activo (2025); unidad con daily-intuition-ty."),
    "mutli-five-sensory": ("improve", "funnel", 1, 4, None, "Activo (2025); arreglar typo de slug; unidad con multi-five-ty."),
    "cultivating-love-optin": ("improve", "funnel", 1, 4, None, "Lead magnet activo (2024)."),
    "cultivating-love-self-assessment": ("consolidate", "consolidate", 1, 4, "cultivating-love-optin", "Variante vieja (2021); fundir en el optin."),
    "authentic-power-support-program-apsp-2025": ("rebuild", "program", 1, 3, None, "Landing APSP; survivor canonico del cluster APSP."),
    "spt-26-registration-fp-2": ("consolidate", "program", 1, 3, None, "Registro SPT 2026 mas nuevo (2025-12); canonico SPT."),
    "spiritual-partnership-program-spt-registration-2026-fp": ("consolidate", "consolidate", 1, 3, "spt-26-registration-fp-2", "Variante 2026; fundir en SPT canonico."),
    "spp-questionnaire": ("improve", "funnel", 1, 3, None, "Intake SPP activo (2025-12)."),
    "apsp-25-registration": ("drop", "redirect", 1, 5, "authentic-power-support-program-apsp-2025", "Cohorte 2025 cerrada."),
    "apsp-23-registration": ("drop", "redirect", 1, 5, "authentic-power-support-program-apsp-2025", "Cohorte 2023 cerrada."),
    "apsp-questionnaire": ("drop", "redirect", 1, 5, "authentic-power-support-program-apsp-2025", "Intake de cohorte APSP cerrada."),
    "spiritual-partnership-program-spp-registration-2025-eb": ("drop", "redirect", 1, 5, None, "SPP 2025 early-bird cerrada."),
    "spiritual-partnership-program-spp-registration-2025-fp": ("drop", "redirect", 1, 5, None, "SPP 2025 full-price cerrada."),
    "spp-25-registration-eb": ("drop", "redirect", 1, 5, None, "Duplicado SPP 2025 EB cerrada."),
    "spp-25-registration-fp": ("drop", "redirect", 1, 5, None, "Duplicado SPP 2025 FP cerrada."),
    "spiritual-partnership-training-program-spt-registration-2025-eb": ("drop", "redirect", 1, 5, "spt-26-registration-fp-2", "SPT 2025 EB cerrada."),
    "spiritual-partnership-training-program-spt-registration-2025-fp": ("drop", "redirect", 1, 5, "spt-26-registration-fp-2", "SPT 2025 FP cerrada."),
    "spt-ground-rules": ("improve", "content", 1, 3, None, "Politica del programa (2025) en uso."),
    "beyond-the-five-senses-course": ("rebuild", "program", 1, 3, None, "Curso; rediseno en marca, confirmar si activo."),
    "beyond-the-five-senses-waitlist": ("consolidate", "consolidate", 1, 3, "beyond-the-five-senses-course", "Waitlist; estado de la pagina del curso."),
    "cultivatingemotionalawareness": ("improve", "content", 1, 4, None, "Programa evergreen (2021); marca + SEO."),
    "intuitivemultisensorylife": ("improve", "content", 1, 4, None, "Programa evergreen (2021); marca + SEO."),
    "journey-to-the-soul-questionnaire": ("improve", "funnel", 1, 3, None, "Intake Journey (2024) recurrente."),
    "journey-questionnaire": ("consolidate", "consolidate", 1, 3, "journey-to-the-soul-questionnaire", "Duplicado viejo (2021)."),
    "journey-to-the-soul-registration-september-2024": ("drop", "redirect", 1, 5, "events-and-programs", "Cohorte Sept-2024 cerrada."),
    "join-the-waitlist-jou23": ("drop", "redirect", 1, 5, None, "Waitlist JOU 2023 cerrada."),
    "event-waitlist-journey-to-the-soul": ("consolidate", "consolidate", 1, 3, "events-and-programs", "Waitlist Journey generico; fundir en programa."),
    "join-the-waitlist-sp-new-dimension-relationship": ("drop", "redirect", 1, 5, None, "Waitlist programa 2022 cerrada."),
    "garyzukavlive": ("improve", "program", 1, 3, None, "Programa recurrente Gary Zukav LIVE; marca + SEO."),
    "garys-welcome-video": ("improve", "content", 1, 4, None, "Video bienvenida evergreen; asset real."),
    "listen-in": ("consolidate", "consolidate", 1, 4, "media", "Pagina audio (2022); fundir con podcast/media."),
    "listen-with-gary-and-linda": ("consolidate", "consolidate", 1, 4, "media", "Pagina audio (2021); fundir con podcast/media."),
    "love-evaluation": ("consolidate", "consolidate", 1, 4, "love-fear", "Assessment (2021); fundir en funnel love-fear."),
    "fear-evaluation": ("consolidate", "consolidate", 1, 4, "love-fear", "Assessment (2021); fundir en funnel love-fear."),
    "universal-human-audiobook-excerpt-chapter-28": ("improve", "content", 1, 4, None, "Excerpt audiolibro evergreen; marca UHF."),
    "universal-human-celebrates-one-year": ("drop", "redirect", 1, 5, None, "Aniversario dated (2022)."),
    "seat-of-the-soul-33rd-anniversary-celebration-giveaway": ("drop", "redirect", 1, 5, None, "Giveaway aniversario dated (2022) expirado."),
    "video-april-2022-event": ("drop", "redirect", 1, 5, None, "Grabacion de evento April-2022."),
    "join-seat-of-the-soul-team": ("consolidate", "consolidate", 1, 3, "seat-of-the-soul-career-opportunities", "Reclutamiento (2021); fundir con careers."),
    "seat-of-the-soul-career-opportunities": ("improve", "content", 1, 3, None, "Careers (2024); survivor de reclutamiento."),
    "jtts-lav-agreement-form": ("improve", "legal", 1, 5, None, "Acuerdo legal de programa (2023); rehacer form."),
    "lav-terms-conditions-agreement": ("consolidate", "consolidate", 1, 5, "jtts-lav-agreement-form", "Terminos LAV viejos (2021); fundir con legal."),

    # ---- System (13) ----
    "privacy-policy": ("keep", "legal", 1, 5, None, "Texto legal actual (2025); portar + shell de marca."),
    "terms-of-use": ("keep", "legal", 1, 5, None, "Texto legal actual (2025); portar + shell."),
    "refund-cancellation": ("keep", "legal", 1, 5, None, "Politica actual (2024); portar + shell."),
    "opt-out": ("improve", "legal", 1, 5, None, "Opt-out email (2024); rehacer integracion de form."),
    "cart": ("drop", "commerce", 1, 5, None, "RIESGO: carrito WooCommerce; sin equivalente nativo Webflow."),
    "checkout": ("drop", "commerce", 1, 5, None, "RIESGO: checkout WooCommerce; gap de plataforma."),
    "my-account": ("drop", "commerce", 1, 5, None, "RIESGO: cuenta de membresia WP; sin equivalente nativo."),
    "your-profile": ("drop", "commerce", 1, 5, None, "RIESGO: perfil de membresia WP; depende de decision."),
    "soul2soulcommunity": ("rebuild", "commerce", 1, 5, None, "RIESGO: membresia/comunidad; Memberstack/Outseta o externo."),
    "evening-welcome": ("drop", "redirect", 1, 5, None, "EWGZ Dashboard interno/evento (2024); no es pagina publica."),
    "sg": ("drop", "redirect", 1, 5, None, "SG Welcome interno/legacy (2023)."),
    "email-series-update": ("drop", "redirect", 1, 5, None, "Utilidad interna de flujo de email (2022)."),
    "style-sheet": ("drop", "redirect", 1, 5, None, "Style reference WP interno; reemplazado por style guide Webflow."),
}

SPRINTS = [
    {"id": 1, "label": "Sprint 1 — Cimientos & Home",
     "goal": "Sistema global (nav, footer, tokens), template TY generico y Home aprobado."},
    {"id": 2, "label": "Sprint 2 — Marca core & Fundadores",
     "goal": "About, Gary, Linda y tributo memorial consolidado (con sign-off del cliente)."},
    {"id": 3, "label": "Sprint 3 — Oferta & Programas",
     "goal": "Hub de programas, landings, registros canonicos e intakes en el form backend elegido."},
    {"id": 4, "label": "Sprint 4 — Funnels & Contenido",
     "goal": "Unidades optin+TY, podcast/media, herramientas, newsletter y contenido evergreen."},
    {"id": 5, "label": "Sprint 5 — Sistema, Legal & Lanzamiento",
     "goal": "Legales, mapa de 301 redirects, QA full-site, decision de commerce/membership y go-live."},
]


def brand_for(slug):
    if slug in UHF:  return "uhf"
    if slug in BOTH: return "both"
    return "sotsi"


def hours_for(archetype, verdict, consolidate_into):
    if verdict == "drop":
        # drops carry only a 301 redirect (tracked, ~0.25h build)
        return {"design": 0, "content": 0, "media": 0, "build": 0.25, "review": 0}
    if verdict == "consolidate" and consolidate_into:
        # a "loser" page merged INTO a survivor: only content extraction + redirect.
        # The survivor (consolidate_into == None) carries the full merge cost.
        return {"design": 0, "content": 1, "media": 0, "build": 0.5, "review": 0}
    d, c, m, b, r = ARCHETYPE_HOURS.get(archetype, ARCHETYPE_HOURS["content"])
    return {"design": d, "content": c, "media": m, "build": b, "review": r}


def build():
    inv = json.load(open(INV, encoding="utf-8"))
    pages = []
    for cat, items in inv["pages_by_category"].items():
        for p in items:
            slug = p["slug"]
            ov = O.get(slug)
            if ov:
                verdict, arche, phase, sprint, cons, note = ov
            else:
                verdict, arche, phase, sprint, cons, note = ("improve", "content", 2, 0, None, "")
            pages.append({
                "slug": slug,
                "url": p["url"],
                "new_path": "/" + slug,            # default; refine in Webflow
                "title": p["title"],
                "brand": brand_for(slug),
                "category": cat,
                "archetype": arche,
                "verdict": verdict,
                "phase": phase,
                "sprint": sprint,
                "status": "backlog",
                "role_hours": hours_for(arche, verdict, cons),
                "content_checklist": {
                    "copy": False, "hero_media": False, "images": False,
                    "video": False, "seo_title": False, "seo_desc": False,
                    "redirects": False,
                },
                "assignee_role": "",
                "dependencies": [],
                "consolidate_into": cons,
                "notes": note,
                "links": {"figma": "", "webflow": ""},
            })

    plan = {
        "meta": {
            "generated_at": "2026-05-25",
            "project": "SOTSI + UHF -> Webflow migration",
            "source_inventory": "data/site_inventory.json",
        },
        "sprints": SPRINTS,
        "pages": sorted(pages, key=lambda x: (x["sprint"] if x["sprint"] else 99, x["slug"])),
    }
    json.dump(plan, open(OUT, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

    # quick console summary
    from collections import Counter
    vc = Counter(p["verdict"] for p in pages)
    pc = Counter(p["phase"] for p in pages)
    th = {r: round(sum(p["role_hours"][r] for p in pages if p["verdict"] != "drop"), 1)
          for r in ["design", "content", "media", "build", "review"]}
    print(f"Wrote {OUT.name}: {len(pages)} pages")
    print("verdicts:", dict(vc))
    print("by phase:", dict(pc))
    print("total build-able hours by role:", th)
    print("grand total hours (excl. drops):", round(sum(th.values()), 1))


if __name__ == "__main__":
    build()
