# SOTSI + UHF — Plan de Migración a Webflow

**Cliente:** Seat of the Soul Institute (seatofthesoul.com) · **Agencia:** 22D Marketing
**Diseño:** Jose (Webflow, plantilla ya comprada) · **Coordinación/Revisión:** Joel
**Fecha del plan:** 2026-05-25 · **Estado:** BORRADOR para revisión de Joel + Jose

> Documento maestro de la migración WordPress → Webflow. Acompaña a:
> - **Tablero del equipo:** `team.html` (KPIs, board filtrable, guía) — se publica en GitHub Pages `/team`.
> - **Datos editables:** `data/migration_plan.json` (fuente de verdad, editable por Claude Code/MCP).
> - **CSV de contenido:** `SOTSI_Migration_Content.csv` · **Redirects:** `SOTSI_Migration_Redirects.csv`.
> - **Marca:** `BRAND_REFERENCE.md` (destilado del Brand Guidelines 2026).

---

## 1. Resumen ejecutivo

El sitio actual en WordPress tiene **110 páginas activas** (+187 posts de blog que migran en una fase posterior). No todas se migran 1-a-1: tras clasificarlas, el sitio destino en Webflow se reduce a **~55 páginas construibles** + un set de redirects.

| Veredicto | Páginas | Qué significa |
|---|---:|---|
| **REBUILD** | 13 | Rediseño nuevo en Webflow (home, about, fundadores, programas ancla, commerce/membership) |
| **IMPROVE** | 39 | Migrar refrescando copy/SEO/media (evergreen + funnels activos) |
| **CONSOLIDATE** | 25 | Fusionar duplicados/variantes en un survivor (3 survivors + 22 que redirigen) |
| **KEEP** | 3 | Portar legal actual con pase de marca (privacy, terms, refund) |
| **DROP** | 30 | No migran; solo 301 redirect (cohortes cerradas, eventos viejos, internas) |
| **TOTAL** | **110** | |

**Carga de trabajo estimada (Fase 1, por rol):**

| Rol | Horas |
|---|---:|
| Build Webflow | 237.5 |
| Contenido / Copy | 214 |
| Diseño (Jose) | 205 |
| Video / Imagen (foto real, no IA) | 144 |
| Revisión (Joel) | 81 |
| **TOTAL** | **≈ 881.5 h** |

> Las horas son envolventes de planeación (caso típico), no compromisos. Excluyen los 30 DROP (solo redirect). El cuello de botella probable es **Video/Imagen** por la regla dura de "fotos reales, nunca IA".

### Grupos de prioridad (cómo está separado el trabajo)

Las páginas están separadas en 4 grupos para atacar primero lo core. En el tablero el board se agrupa así y hay filtro por grupo.

| Grupo | Págs a construir | Horas | Qué incluye |
|---|--:|--:|---|
| **1 · Páginas principales** | 14 | 247.5 | Lo que sí o sí debe estar al lanzar: home, about, fundadores, books, get-started, events&programs, podcast, media, faqs, connect, newsletter, blog (índice) |
| **2 · Programas y funnels** | 42 | 420.5 | Programas (APSP, SPT, SPP, Journey, Beyond 5 Senses, courses), registros canónicos, optins+TY, evaluaciones |
| **3 · Contenido y evergreen** | 18 | 123.5 | Ensayos/teaching (Heart of the Soul, Universal Human, AI & Human Evolution…), tributo memorial Linda |
| **4 · Sistema y legal** | 6 | 90.0 | Privacy, Terms, Refund, Opt-out + commerce/membership (RIESGO) |

> **Nota sobre "fáciles":** dentro de Principales hay quick-wins (FAQs, Connect, Media ≈ 5–18h c/u) y piezas pesadas (Home ≈ 42h, About/fundadores ≈ 23h c/u). Son las **esenciales**, no todas triviales — pero son el orden correcto para arrancar.

> **Blog (187 posts) = Fase 2, plan aparte.** Ya está triado (167 keep / 20 drop). Aquí es donde tienes dudas; lo trabajamos por separado cuando quieras.

---

## 2. Decisiones ya tomadas (Joel)

1. **Alcance:** Fase 1 = **sitio principal**. El blog (187 posts, ya triado: 167 keep / 20 drop) es fase posterior.
2. **Estimación:** **por rol**, no por persona. Joel reparte después.
3. **Tablero:** sitio estático con la marca nueva en **GitHub Pages**, alimentado por `migration_plan.json`. Sin BD, sin backend, gratis. Joel/Claude actualizan estatus editando el JSON y republicando.

---

## 3. Rúbrica de clasificación

Cada página recibe el primer veredicto que cumple, de arriba hacia abajo:

| Veredicto | Criterio (cualquiera lo dispara) |
|---|---|
| **DROP** | Atada a evento/año pasado que no se repite igual; superada por una variante más nueva; página interna/legacy; sub-página de un momento único ya vencido. → 301 redirect. |
| **CONSOLIDATE** | Slug duplicado (`blog`/`blog-2`); mismo programa en variantes de año/precio (EB/FP, 2025/2026); cluster que cuenta una sola narrativa (memorial Linda); contenido casi idéntico con otro slug. |
| **REBUILD** | Página de alto tráfico o que define la marca; estructuralmente compleja (hub, home, índice); fuera de la marca 2026. Default de lo que carga peso. |
| **IMPROVE** | Contenido vigente y sano que solo necesita: fix de meta/título, swap de foto real (no IA), alineación de fuente/color, pulido ligero de copy. |
| **KEEP** | Texto legal/utilitario vigente y correcto; solo pase de marca al shell. (Raro al cambiar de plataforma.) |

**Reglas de oro:**
- Un `*-optin` / `*-questionnaire` / `*-evaluation` y su `*-ty` (thank-you) son **UNA unidad de trabajo**.
- La fecha de modificación es señal, no veredicto: una legal de 2021 puede ser KEEP; un evento de 2024 puede ser DROP.
- Cuando un programa existe como landing + variante de registro/pago, la **landing es el survivor**; las variantes por año/precio se consolidan o se dropean si la cohorte está cerrada.

---

## 4. Modelo de horas por arquetipo (caso típico)

Orden: Diseño · Contenido · Video/Imagen · Build · Revisión.

| Arquetipo | Dis | Cont | Media | Build | Rev | Total |
|---|--:|--:|--:|--:|--:|--:|
| Componentes globales (nav/footer/tokens) — una vez | 10 | 2 | 2 | 12 | 3 | 29 |
| Hub complejo (Home) | 12 | 6 | 8 | 12 | 4 | 42 |
| Índice / navegación (Events, Get Started, Media) | 5 | 3 | 3 | 5 | 2 | 18 |
| Programa / Landing (APSP, SPT, Books, Courses) | 6 | 5 | 4 | 6 | 2 | 23 |
| Bio fundador / memorial | 5 | 6 | 5 | 5 | 2 | 23 |
| Unidad funnel (optin + TY) | 3 | 3 | 2 | 3 | 1 | 12 |
| Página de contenido simple (ensayo/teaching) | 2 | 3 | 2 | 2 | 1 | 10 |
| Survivor de consolidación (fusiona N → 1) | 5 | 6 | 4 | 5 | 2 | 22 |
| Template reusable (confirmación/TY genérico) | 2 | 1 | 1 | 3 | 1 | 8 |
| Legal / sistema | 1 | 1 | 0 | 2 | 1 | 5 |
| Commerce / Membership (RIESGO, spike) | 8 | 4 | 4 | 16 | 3 | 35+ |

Notas: la consolidación cuesta más en **Contenido** (fusionar narrativas) que en Diseño. Las horas de commerce/membership son placeholder hasta decidir plataforma.

---

## 5. Plan de 5 sprints (Fase 1)

Ordenados por dependencia. Nada se finaliza hasta que los **componentes globales** estén lockeados.

### Sprint 1 — Cimientos & Home
Sistema global (nav, footer, tokens de marca, style guide), template TY genérico, **Home**.
**Salida:** nav/footer como símbolos reusables; tokens (navy/purple, Canela/Jost) como estilos globales; Home aprobada por Joel→cliente.

### Sprint 2 — Marca core & Fundadores
About, About Gary Zukav, About Linda Francis, **tributo memorial consolidado** (absorbe 8 páginas del cluster Linda), Seat of the Soul Institute → fundir en About.
**Entrada:** globales lockeados + **sign-off del cliente sobre la consolidación memorial** (contenido sensible). **Salida:** redirects del cluster mapeados; fotos reales de fundadores conseguidas (no IA).

### Sprint 3 — Oferta & Programas
Hub Events & Programs, Get Started, Books, Courses–LightEn, Beyond the Five Senses, APSP landing, SPT 2026 registro, SPP questionnaire, Journey programa+intake, Careers.
**Entrada:** decisión de commerce conocida (afecta paths de compra). **Salida:** variantes de cohortes cerradas redirigidas; formularios conectados al backend elegido.

### Sprint 4 — Funnels & Contenido
Todas las unidades optin+TY (apg, daily-intuition, cultivating-love, multi-five-sensory, love-fear, responsible-choice, addiction, judgment), Podcast (+subscribe), Media (+listen), Free Tools, Newsletter (+archive), FAQs, Connect, Heart of the Soul, Universal Human, ensayos evergreen.
**Salida:** cada optin con form funcional + TY; SEO meta por página; media real swapeada.

### Sprint 5 — Sistema, Legal & Lanzamiento
Privacy, Terms, Refund, Opt-out; **mapa completo de 301 redirects** (51 URLs); QA full-site (responsive/links/marca); decisión de commerce/membership ejecutada o placeholder; **reservar estructura de URL del blog** aunque su build sea posterior.

---

## 6. Definition of Done (por página)

Una página pasa a *done* solo con todo esto:

- [ ] **Marca:** marca correcta (SOTSI navy/naturaleza vs UHF purple/humanos); colores en rango; amarillo solo de acento; Canela títulos / Jost cuerpo.
- [ ] **Media:** foto/video real (no IA), alta resolución, crop intencional; regla correcta (SOTSI montaña/agua sin arena; UHF rostros).
- [ ] **Contenido:** copy revisado y vigente (sin fechas muertas/cohortes cerradas); tono calmado; CTA a destino vivo.
- [ ] **SEO:** title 30–65 car.; meta 120–160; un H1; 3+ links internos; alt text completo.
- [ ] **Responsive:** 320 / 375 / 768 / 1024 / 1440 sin overflow.
- [ ] **Links/forms:** todo resuelve; forms disparan el TY correcto; tracking puesto.
- [ ] **Redirect:** URL vieja registrada con su 301 en el mapa.
- [ ] **Sign-off:** Joel revisó con Jose; aprobación de cliente donde aplique (fundadores / memorial Linda = obligatorio).

---

## 7. Riesgos y dependencias críticas

1. **E-commerce (CRÍTICO).** `shop`/`cart`/`checkout` corren en WooCommerce; Webflow no tiene equivalente nativo de esa profundidad. Decidir: Webflow Ecommerce vs Foxy/Shopify-Buy vs mantener tienda WP en subdominio. **Bloquea Books/Courses. Resolver antes del Sprint 3.**
2. **Membresía/Comunidad (CRÍTICO).** `soul2soulcommunity`, `my-account`, `your-profile` son features de membresía WP. Webflow necesita Memberstack/Outseta o plataforma externa. Si no se resuelve, Fase 1 lanza con placeholder → Fase 1.5.
3. **Backend de formularios (ALTO).** Muchos questionnaires/optins/acuerdos dependen de plugins WP + automatización de email. Forms de Webflow tienen límites (lógica, upload, integraciones). Elegir backend (Webflow nativo + Zapier/Make, o embed) temprano.
4. **Mapa de 301 redirects para SEO (ALTO).** 30 DROP + 21 consolidate-losers = **51 URLs** que deben redirigir. Un mapa roto al cutover destruye el SEO existente. Se construye incrementalmente (está en el DoD) y se despliega en el Sprint 5. Ya generado en `SOTSI_Migration_Redirects.csv`.
5. **Licencia de fuente Canela (MEDIO-ALTO).** La marca exige Canela (licencia comercial). Confirmar licencia web antes de producción; el fallback (Cormorant) es solo temporal.
6. **Sourcing de foto real, no-IA (ALTO).** Regla dura de marca. Es el slip de calendario más probable. Montar una biblioteca de assets aprobados desde Sprint 1–2.
7. **Sensibilidad del contenido memorial (MEDIO).** Consolidar 8 páginas de Linda + birthday/wishes de Gary en un tributo requiere **sign-off explícito del cliente**. No auto-dropear. Gate del Sprint 2.
8. **Estructura de URL del blog (MEDIO).** El blog se difiere, pero el esquema `/blog/...` y el índice canónico (`blog`, drop `blog-2`) deben decidirse en Fase 1 para no rehacer redirects e IA después.

**Data-quality a corregir en el rebuild:** slug `judgment` vs `judgement-thank-you`, typo `mutli-five-sensory`, sufijo `-fp-2` en SPT 2026. Normalizar slugs y guardar los viejos en el mapa de redirects.

---

## 8. Flujo de trabajo del equipo

```
Joel/Claude editan  data/migration_plan.json  (estatus, horas, checklist, asignaciones)
        │
        ▼
python3 build_migration_dashboard.py   →  team.html   (tablero, GitHub Pages /team)
python3 generate_migration_csv.py      →  CSVs de contenido + redirects
        │
        ▼
git add -A && git commit && git push    →  live en ~1 min
```

- **Contenido vía MCP:** el equipo trabaja sobre `SOTSI_Migration_Content.csv`; los cambios vuelven a `migration_plan.json` (editado por Claude Code/MCP). Regenerar es idempotente.
- **Estatus de una página:** cambiar `status` (`backlog`→`design`→`content`→`build`→`review`→`done`, o `blocked`) y marcar el `content_checklist`. El tablero recalcula KPIs y barras solo.

---

## 9. Próximos pasos sugeridos

1. **Joel + Jose revisan este plan** y el board (`team.html`) — confirmar veredictos sensibles (memorial Linda, qué páginas DROP).
2. **Decisión de commerce + membership** (riesgos 1 y 2) — bloquea Sprint 3.
3. **Confirmar licencia de Canela** y montar biblioteca de fotos reales.
4. Publicar el tablero en GitHub Pages y compartir la URL con el equipo.
5. Arrancar Sprint 1 (componentes globales + Home).
