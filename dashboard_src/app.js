/* SOTSI/UHF migration dashboard — client app.
   Data (PAGES, SPRINTS, PLANS) is injected by build_migration_dashboard.py.
   Everything user-facing is bilingual ES/EN via the I18N dict + applyI18n(). */

const ROLES = ["design", "content", "media", "build", "review"];
const GROUP_ORDER = ["principales", "programas", "contenido", "sistema"];
const STATUSES = ["backlog", "design", "content", "build", "review", "done", "blocked"];

const ROLE_LABELS = {
  es: { design: "Diseño", content: "Contenido", media: "Video/Imagen", build: "Build Webflow", review: "Revisión" },
  en: { design: "Design", content: "Content", media: "Video/Image", build: "Webflow Build", review: "Review" },
};
const GROUP_LABELS = {
  es: { principales: "1 · Páginas principales", programas: "2 · Programas y funnels", contenido: "3 · Contenido y evergreen", sistema: "4 · Sistema y legal" },
  en: { principales: "1 · Main pages", programas: "2 · Programs & funnels", contenido: "3 · Content & evergreen", sistema: "4 · System & legal" },
};
const STATUS_LABELS = {
  es: { backlog: "Backlog", design: "Diseño", content: "Contenido", build: "Build", review: "Revisión", done: "Done", blocked: "Bloqueada" },
  en: { backlog: "Backlog", design: "Design", content: "Content", build: "Build", review: "Review", done: "Done", blocked: "Blocked" },
};
const VERDICT_LABELS = {
  es: { keep: "Keep", improve: "Improve", rebuild: "Rebuild", consolidate: "Consolidate", drop: "Drop" },
  en: { keep: "Keep", improve: "Improve", rebuild: "Rebuild", consolidate: "Consolidate", drop: "Drop" },
};
const ACTION_LABELS = {
  es: { reconstruir: "Reconstruir", mejorar: "Mejorar", consolidar: "Consolidar", mantener: "Mantener", agregar: "Agregar", quitar: "Quitar" },
  en: { reconstruir: "Rebuild", mejorar: "Improve", consolidar: "Consolidate", mantener: "Keep", agregar: "Add", quitar: "Remove" },
};

const I18N = {
  es: {
    "h.title_html": 'Plan de Migración a <em>Webflow</em>',
    "h.brandline": "Seat of the Soul · Universal Human · 22D Marketing",
    "h.sub": "Tablero de trabajo del equipo — qué se mantiene, mejora, reconstruye o elimina, con horas por rol y avance por sprint.",
    "h.updated": "Actualizado:",
    "tab.overview": "Resumen", "tab.board": "Board", "tab.guide": "Guía del equipo",
    "kpi.done": "Avance", "kpi.hours": "Horas restantes", "kpi.prog": "En progreso", "kpi.blocked": "Bloqueadas", "kpi.pages": "Páginas a construir",
    "kpi.done_sub": "{a} de {b} páginas", "kpi.hours_sub": "de {a}h totales", "kpi.prog_sub": "design / content / build / review",
    "kpi.blocked_sub": "necesitan decisión", "kpi.pages_sub": "{a} drops (solo redirect)",
    "ov.plans_title": "Planes de página", "ov.plans_note": "Plan de acción detallado por página. Empezamos por Home; al dar click se abre su mini-dashboard de secciones.",
    "ov.open_plan": "Abrir plan →",
    "ov.groups_title": "Grupos de prioridad",
    "ov.groups_note": "Principales = páginas core que sí o sí deben estar al lanzar (home, about, nav). El blog (187 posts) es Fase 2 aparte.",
    "ov.sprints_title": "Sprints", "ov.roles_title": "Horas por rol — avance",
    "ov.roles_note": "Barras = horas done sobre horas totales estimadas (excluye drops, que solo llevan 301 redirect).",
    "grp.build": "a construir", "grp.drops": "drops", "grp.total": "en total", "grp.done": "done", "spr.pages": "págs", "spr.done": "done",
    "f.group": "Grupo: todos", "f.status": "Estatus: todos", "f.sprint": "Sprint: todos", "f.verdict": "Veredicto: todos",
    "f.brand": "Marca: todas", "f.cat": "Categoría: todas", "f.search_ph": "Buscar título o slug…", "f.clear": "Limpiar", "f.showing": "Mostrando {a} de {b}",
    "f.sprint_n": "Sprint {a}",
    "col.status": "Estatus", "col.title": "Título", "col.brand": "Marca", "col.cat": "Categoría", "col.verdict": "Veredicto",
    "col.sprint": "Sprint", "col.checklist": "Checklist", "col.hours": "Horas", "col.see": "Vieja",
    "see.old": "Ver ↗",
    "p.see_old": "Ver página vieja ↗", "p.open_plan": "Abrir plan de la página →",
    "p.urls": "URL vieja → nueva", "p.meta": "Categoría / Sprint / Arquetipo", "p.cons": "Se consolida en",
    "p.checklist": "Content checklist", "p.hours": "Horas estimadas por rol", "p.total": "Total", "p.notes": "Notas", "p.links": "Enlaces", "p.slug": "Slug",
    "pm.eyebrow": "Plan de la página", "pm.base": "Base", "pm.ai_tag": "Contexto por IA", "pm.verdict": "Veredicto",
    "pm.sections": "Mapa de secciones · Home original (WordPress) → Webflow",
    "pm.note_local": "Los checks se guardan solo en este navegador. Para persistir en el equipo, edita data/page_plans.json y regenera.",
    "pm.done_count": "{a}/{b} secciones listas",
    "pm.col_section": "Sección", "pm.col_old": "Esqueleto viejo (WordPress)", "pm.col_new": "Esqueleto nuevo (Webflow)",
    "pm.col_action": "Acción", "pm.col_wf": "Mapeado a Webflow", "pm.col_notes": "Notas", "pm.col_hrs": "Horas", "pm.col_done": "OK",
    "pm.tpl_global": "Componentes globales", "pm.tpl_blocks": "Bloques reutilizables", "pm.tpl_strip": "Quitar / arreglar", "pm.tpl_tokens": "Tokens & re-skin",
    "g.title": "Guía del equipo",
  },
  en: {
    "h.title_html": '<em>Webflow</em> Migration Plan',
    "h.brandline": "Seat of the Soul · Universal Human · 22D Marketing",
    "h.sub": "Team work board — what we keep, improve, rebuild or drop, with hours by role and progress by sprint.",
    "h.updated": "Updated:",
    "tab.overview": "Overview", "tab.board": "Board", "tab.guide": "Team guide",
    "kpi.done": "Progress", "kpi.hours": "Hours remaining", "kpi.prog": "In progress", "kpi.blocked": "Blocked", "kpi.pages": "Pages to build",
    "kpi.done_sub": "{a} of {b} pages", "kpi.hours_sub": "of {a}h total", "kpi.prog_sub": "design / content / build / review",
    "kpi.blocked_sub": "need a decision", "kpi.pages_sub": "{a} drops (redirect only)",
    "ov.plans_title": "Page plans", "ov.plans_note": "Detailed per-page action plan. We start with Home; click to open its section mini-dashboard.",
    "ov.open_plan": "Open plan →",
    "ov.groups_title": "Priority groups",
    "ov.groups_note": "Main pages = core pages that must ship at launch (home, about, nav). The blog (187 posts) is a separate Phase 2.",
    "ov.sprints_title": "Sprints", "ov.roles_title": "Hours by role — progress",
    "ov.roles_note": "Bars = done hours over total estimated hours (excludes drops, which only get a 301 redirect).",
    "grp.build": "to build", "grp.drops": "drops", "grp.total": "total", "grp.done": "done", "spr.pages": "pages", "spr.done": "done",
    "f.group": "Group: all", "f.status": "Status: all", "f.sprint": "Sprint: all", "f.verdict": "Verdict: all",
    "f.brand": "Brand: all", "f.cat": "Category: all", "f.search_ph": "Search title or slug…", "f.clear": "Clear", "f.showing": "Showing {a} of {b}",
    "f.sprint_n": "Sprint {a}",
    "col.status": "Status", "col.title": "Title", "col.brand": "Brand", "col.cat": "Category", "col.verdict": "Verdict",
    "col.sprint": "Sprint", "col.checklist": "Checklist", "col.hours": "Hours", "col.see": "Old",
    "see.old": "View ↗",
    "p.see_old": "View old page ↗", "p.open_plan": "Open page plan →",
    "p.urls": "Old → new URL", "p.meta": "Category / Sprint / Archetype", "p.cons": "Consolidates into",
    "p.checklist": "Content checklist", "p.hours": "Estimated hours by role", "p.total": "Total", "p.notes": "Notes", "p.links": "Links", "p.slug": "Slug",
    "pm.eyebrow": "Page plan", "pm.base": "Base", "pm.ai_tag": "AI context", "pm.verdict": "Verdict",
    "pm.sections": "Section map · Original Home (WordPress) → Webflow",
    "pm.note_local": "Checks are saved in this browser only. To persist for the team, edit data/page_plans.json and rebuild.",
    "pm.done_count": "{a}/{b} sections done",
    "pm.col_section": "Section", "pm.col_old": "Old skeleton (WordPress)", "pm.col_new": "New skeleton (Webflow)",
    "pm.col_action": "Action", "pm.col_wf": "Mapped to Webflow", "pm.col_notes": "Notes", "pm.col_hrs": "Hours", "pm.col_done": "OK",
    "pm.tpl_global": "Global components", "pm.tpl_blocks": "Reusable blocks", "pm.tpl_strip": "Strip / fix", "pm.tpl_tokens": "Tokens & re-skin",
    "g.title": "Team guide",
  },
};

let LANG = localStorage.getItem("sotsi_lang") || "es";

const esc = (s) => (s == null ? "" : String(s)).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const t = (k) => (I18N[LANG][k] != null ? I18N[LANG][k] : (I18N.es[k] != null ? I18N.es[k] : k));
const tf = (k, vals) => { let s = t(k); for (const [kk, vv] of Object.entries(vals)) s = s.replace("{" + kk + "}", vv); return s; };
const cap = (s) => (s ? s[0].toUpperCase() + s.slice(1) : s);
const pageHours = (p) => ROLES.reduce((a, r) => a + (p.role_hours[r] || 0), 0);
const statusL = (s) => STATUS_LABELS[LANG][s] || cap(s);
const verdictL = (v) => VERDICT_LABELS[LANG][v] || cap(v);
const actionL = (a) => ACTION_LABELS[LANG][a] || cap(a);
const roleL = (r) => ROLE_LABELS[LANG][r] || r;
const groupL = (g) => GROUP_LABELS[LANG][g] || g;

/* ── meta rollups (ported from compute_meta) ─────────────────────────────── */
function computeMeta() {
  const buildable = PAGES.filter((p) => p.verdict !== "drop");
  const done = PAGES.filter((p) => p.status === "done");
  const roleTotal = {}, roleDone = {};
  ROLES.forEach((r) => {
    roleTotal[r] = Math.round(buildable.reduce((a, p) => a + (p.role_hours[r] || 0), 0) * 10) / 10;
    roleDone[r] = Math.round(done.reduce((a, p) => a + (p.role_hours[r] || 0), 0) * 10) / 10;
  });
  const totalH = Math.round(Object.values(roleTotal).reduce((a, b) => a + b, 0) * 10) / 10;
  const doneH = Math.round(Object.values(roleDone).reduce((a, b) => a + b, 0) * 10) / 10;
  const byStatus = {}; STATUSES.forEach((s) => (byStatus[s] = PAGES.filter((p) => p.status === s).length));
  const drops = PAGES.filter((p) => p.verdict === "drop").length;
  return {
    total: PAGES.length, buildable: buildable.length, byStatus, drops,
    roleTotal, roleDone, totalH, doneH, remaining: Math.round((totalH - doneH) * 10) / 10,
    pctDone: PAGES.length ? Math.round((done.length / PAGES.length) * 1000) / 10 : 0,
  };
}

/* ── dynamic renderers (re-run on language change) ───────────────────────── */
function renderKpis(m) {
  const inProg = ["design", "content", "build", "review"].reduce((a, s) => a + (m.byStatus[s] || 0), 0);
  const cards = [
    ["done", m.pctDone + "%", t("kpi.done"), tf("kpi.done_sub", { a: m.byStatus.done, b: m.total })],
    ["hours", (+m.remaining) + "h", t("kpi.hours"), tf("kpi.hours_sub", { a: +m.totalH })],
    ["prog", String(inProg), t("kpi.prog"), t("kpi.prog_sub")],
    ["blocked", String(m.byStatus.blocked), t("kpi.blocked"), t("kpi.blocked_sub")],
    ["pages", String(m.buildable), t("kpi.pages"), tf("kpi.pages_sub", { a: m.drops })],
  ];
  document.getElementById("kpis").innerHTML = cards.map(([k, v, l, s]) =>
    `<div class="kpi kpi-${k}"><div class="kpi-val">${v}</div><div class="kpi-label">${esc(l)}</div><div class="kpi-sub">${esc(s)}</div></div>`).join("");
}

function renderBars(m) {
  document.getElementById("role-bars").innerHTML = ROLES.map((r) => {
    const tot = m.roleTotal[r] || 0, dn = m.roleDone[r] || 0, pct = tot ? Math.round((dn / tot) * 100) : 0;
    return `<div class="bar-row"><div class="bar-head"><span>${esc(roleL(r))}</span><span class="bar-num">${dn} / ${tot}h</span></div>
      <div class="bar-track"><div class="bar-fill" style="width:${pct}%"></div></div></div>`;
  }).join("");
}

function renderSprints() {
  document.getElementById("sprint-tiles").innerHTML = SPRINTS.map((s) => {
    const sp = PAGES.filter((p) => p.sprint === s.id);
    const done = sp.filter((p) => p.status === "done").length;
    const hrs = Math.round(sp.filter((p) => p.verdict !== "drop").reduce((a, p) => a + pageHours(p), 0) * 10) / 10;
    const pct = sp.length ? Math.round((done / sp.length) * 100) : 0;
    return `<div class="sprint-tile"><div class="sprint-id">${esc(s.label)}</div><div class="sprint-goal">${esc(s.goal)}</div>
      <div class="sprint-meta"><span>${sp.length} ${t("spr.pages")}</span><span>${hrs}h</span><span>${done}/${sp.length} ${t("spr.done")}</span></div>
      <div class="bar-track sm"><div class="bar-fill" style="width:${pct}%"></div></div></div>`;
  }).join("");
}

function renderGroups() {
  document.getElementById("group-summary").innerHTML = GROUP_ORDER.map((g) => {
    const gp = PAGES.filter((p) => p.group === g); if (!gp.length) return "";
    const buildable = gp.filter((p) => p.verdict !== "drop");
    const done = gp.filter((p) => p.status === "done").length;
    const hrs = Math.round(buildable.reduce((a, p) => a + pageHours(p), 0) * 10) / 10;
    const pct = gp.length ? Math.round((done / gp.length) * 100) : 0;
    const drops = gp.filter((p) => p.verdict === "drop").length;
    return `<div class="grp-card grp-${g}"><div class="grp-title">${esc(groupL(g))}</div>
      <div class="grp-big">${buildable.length}<span> ${t("grp.build")}</span></div>
      <div class="grp-meta">${hrs}h · ${drops} ${t("grp.drops")} · ${gp.length} ${t("grp.total")}</div>
      <div class="bar-track sm"><div class="bar-fill" style="width:${pct}%"></div></div>
      <div class="grp-pct">${done}/${gp.length} ${t("grp.done")}</div></div>`;
  }).join("");
}

function renderPlansList() {
  const slugs = Object.keys(PLANS || {}).filter((k) => k !== "_comment");
  const el = document.getElementById("plans-list");
  if (!slugs.length) { el.innerHTML = ""; return; }
  el.innerHTML = slugs.map((slug) => {
    const p = PAGES.find((x) => x.slug === slug); if (!p) return "";
    const secs = (PLANS[slug].sections || []).length;
    return `<button class="grp-card" style="text-align:left;cursor:pointer;border-top-color:var(--gold-yellow)" onclick="openPlanBySlug('${esc(slug)}')">
      <div class="grp-title">${esc(p.title)}</div>
      <div class="grp-big">${secs}<span> ${LANG === "es" ? "secciones" : "sections"}</span></div>
      <div class="grp-meta">${pageHours(p)}h · ${esc(verdictL(p.verdict))}</div>
      <div class="lk-btn plan" style="margin-top:6px">${esc(t("ov.open_plan"))}</div></button>`;
  }).join("");
}

/* ── guide (bilingual, rendered in JS) ───────────────────────────────────── */
function renderGuide() {
  const sw = [["Midnight Navy", "#0E1631"], ["Cosmic Purple", "#3C1951"], ["Pure White", "#FFFFFF"],
    ["Soft Periwinkle", "#D2CCFD"], ["Light Lilac", "#E7D4F1"], ["Luminous Yellow", "#FFEB45"], ["Golden Yellow", "#FED457"]];
  const chips = sw.map(([n, h]) => `<div class="sw"><span class="sw-box" style="background:${h}"></span><span class="sw-name">${n}</span><span class="sw-hex">${h}</span></div>`).join("");
  const G = {
    es: {
      c1: "1 · Reglas de marca", c2: "2 · Flujo de producción de contenido (por página)", c3: "3 · Definition of Done (checklist por página)",
      b1: `<p><b>Dos marcas, un sistema.</b> SOTSI = Midnight Navy + naturaleza (montañas/agua, <u>nunca</u> arena). UHF = Cosmic Purple + rostros humanos, close-ups diversos.</p><div class="sw-grid">${chips}</div>
        <p><b>Tipografía:</b> Títulos = <i>Canela</i> (serif) · Cuerpo = <i>Jost</i> (sans) · Acento = <i>WorldDiscovery One</i> (script, solo frases emotivas, sin números).</p>
        <p><b>Regla dura:</b> fotos/video <b>reales, NUNCA IA</b>; alta resolución; crop intencional; esquinas redondeadas; whitespace generoso; tono calmado y claro, sin urgencia.</p>
        <p class="g-ref">Detalle completo en <code>BRAND_REFERENCE.md</code>.</p>`,
      b2: `<ol><li><b>Leer la página vieja</b> en WordPress (botón "Ver" del board).</li><li><b>Escribir el copy nuevo</b> con la voz de marca (claro, profundo, sin urgencia).</li>
        <li><b>Conseguir/solicitar media real</b> — foto o video (no IA), regla de marca correcta.</li><li><b>Construir en Webflow</b> sobre los componentes globales (nav/footer/tokens).</li>
        <li><b>SEO:</b> title 30–65 car., meta description 120–160, 1 H1, alt text, 3+ links internos.</li><li><b>Mapear el 301 redirect</b> de la URL vieja a la nueva.</li></ol>`,
      b3: `<ul><li><b>copy</b> — texto nuevo escrito y revisado, sin fechas muertas.</li><li><b>hero_media</b> — imagen/video hero real (no IA), alta resolución.</li>
        <li><b>images</b> — imágenes de cuerpo con alt text.</li><li><b>video</b> — video embebido donde aplique.</li><li><b>seo_title / seo_desc</b> — meta dentro de rango.</li>
        <li><b>redirects</b> — 301 de URL vieja registrado.</li><li>Responsive 320/375/768/1024/1440 · links/forms OK · sign-off Joel+Jose.</li></ul>`,
    },
    en: {
      c1: "1 · Brand rules", c2: "2 · Content production flow (per page)", c3: "3 · Definition of Done (per-page checklist)",
      b1: `<p><b>Two brands, one system.</b> SOTSI = Midnight Navy + nature (mountains/water, <u>never</u> sand). UHF = Cosmic Purple + human faces, diverse close-ups.</p><div class="sw-grid">${chips}</div>
        <p><b>Typography:</b> Headings = <i>Canela</i> (serif) · Body = <i>Jost</i> (sans) · Accent = <i>WorldDiscovery One</i> (script, emotive phrases only, no numbers).</p>
        <p><b>Hard rule:</b> <b>real photos/video, NEVER AI</b>; high resolution; intentional crop; rounded corners; generous whitespace; calm, clear tone, no urgency.</p>
        <p class="g-ref">Full detail in <code>BRAND_REFERENCE.md</code>.</p>`,
      b2: `<ol><li><b>Read the old page</b> on WordPress (board "View" button).</li><li><b>Write the new copy</b> in brand voice (clear, deep, no urgency).</li>
        <li><b>Source/request real media</b> — photo or video (no AI), correct brand rule.</li><li><b>Build in Webflow</b> on the global components (nav/footer/tokens).</li>
        <li><b>SEO:</b> title 30–65 chars, meta description 120–160, 1 H1, alt text, 3+ internal links.</li><li><b>Map the 301 redirect</b> from old URL to new.</li></ol>`,
      b3: `<ul><li><b>copy</b> — new text written and reviewed, no dead dates.</li><li><b>hero_media</b> — real hero image/video (no AI), high resolution.</li>
        <li><b>images</b> — body images with alt text.</li><li><b>video</b> — embedded video where it applies.</li><li><b>seo_title / seo_desc</b> — meta in range.</li>
        <li><b>redirects</b> — old URL 301 registered.</li><li>Responsive 320/375/768/1024/1440 · links/forms OK · Joel+Jose sign-off.</li></ul>`,
    },
  }[LANG];
  document.getElementById("guide").innerHTML = `
    <details open class="g-card"><summary>${G.c1}</summary><div class="g-body">${G.b1}</div></details>
    <details class="g-card"><summary>${G.c2}</summary><div class="g-body">${G.b2}</div></details>
    <details class="g-card"><summary>${G.c3}</summary><div class="g-body">${G.b3}</div></details>`;
}

/* ── static-chrome i18n + filter selects ─────────────────────────────────── */
function applyI18n() {
  document.documentElement.lang = LANG;
  document.querySelectorAll("[data-i18n]").forEach((el) => { el.textContent = t(el.dataset.i18n); });
  document.querySelectorAll("[data-i18n-html]").forEach((el) => { el.innerHTML = t(el.dataset.i18nHtml); });
  document.querySelectorAll("[data-i18n-ph]").forEach((el) => { el.placeholder = t(el.dataset.i18nPh); });
  document.querySelectorAll(".lang-toggle button").forEach((b) => b.classList.toggle("active", b.dataset.lang === LANG));
}

function populateFilters() {
  const defs = { "f-group": "f.group", "f-status": "f.status", "f-sprint": "f.sprint", "f-verdict": "f.verdict", "f-brand": "f.brand", "f-cat": "f.cat" };
  const fill = (id, vals, labelFn) => {
    const sel = document.getElementById(id), cur = sel.value;
    sel.innerHTML = `<option value="">${esc(t(defs[id]))}</option>`;
    vals.forEach((v) => { const o = document.createElement("option"); o.value = v; o.textContent = labelFn ? labelFn(v) : v; sel.appendChild(o); });
    sel.value = cur;
  };
  fill("f-group", GROUP_ORDER.filter((g) => PAGES.some((p) => p.group === g)), groupL);
  fill("f-status", [...new Set(PAGES.map((p) => p.status))].sort(), statusL);
  fill("f-sprint", [...new Set(PAGES.map((p) => p.sprint))].sort((a, b) => a - b), (v) => tf("f.sprint_n", { a: v }));
  fill("f-verdict", [...new Set(PAGES.map((p) => p.verdict))].sort(), verdictL);
  fill("f-brand", [...new Set(PAGES.map((p) => p.brand))].sort(), (v) => v.toUpperCase());
  fill("f-cat", [...new Set(PAGES.map((p) => p.category))].sort());
}

/* ── board (Tabulator) ───────────────────────────────────────────────────── */
const badge = (cls, txt) => `<span class="badge ${cls}">${esc(txt)}</span>`;

function makeColumns() {
  return [
    { title: t("col.status"), field: "status", width: 104, formatter: (c) => badge("st-" + c.getValue(), statusL(c.getValue())) },
    { title: t("col.title"), field: "title", minWidth: 190, formatter: (c) => {
        const d = c.getData(); const dot = pagePlan(d) ? `<span class="has-plan-dot" title="Tiene plan"></span>` : "";
        return `<b>${esc(c.getValue())}</b>${dot}<br><span style="color:#7a748f;font-size:11px">/${esc(d.slug)}</span>`; } },
    { title: t("col.see"), field: "url", width: 78, hozAlign: "center", headerSort: false, formatter: () => `<span class="see-old">${esc(t("see.old"))}</span>`,
      cellClick: (e, cell) => { e.stopPropagation(); const u = cell.getData().url; if (u) window.open(u, "_blank", "noopener"); } },
    { title: t("col.brand"), field: "brand", width: 74, hozAlign: "center", formatter: (c) => badge("br-" + c.getValue(), c.getValue().toUpperCase()) },
    { title: t("col.cat"), field: "category", width: 128 },
    { title: t("col.verdict"), field: "verdict", width: 116, formatter: (c) => badge("vd-" + c.getValue(), verdictL(c.getValue())) },
    { title: t("col.sprint"), field: "sprint", width: 72, hozAlign: "center" },
    { title: t("col.checklist"), field: "slug", width: 92, hozAlign: "center", headerSort: false, formatter: (c) => {
        const ck = c.getData().content_checklist, keys = Object.keys(ck), n = keys.filter((k) => ck[k]).length, pct = Math.round((n / keys.length) * 100);
        return `<div style="font-size:11px">${n}/${keys.length}</div><div class="bar-track sm" style="margin-top:3px"><div class="bar-fill" style="width:${pct}%"></div></div>`; } },
    { title: t("col.hours"), field: "slug", width: 70, hozAlign: "right", headerSort: false, formatter: (c) => pageHours(c.getData()) + "h" },
  ];
}

function buildTable() {
  if (window.table) { window.table.destroy(); }
  const table = new Tabulator("#board", {
    data: PAGES, layout: "fitColumns", height: "calc(100vh - 300px)", reactiveData: false,
    groupBy: "group", groupValues: [GROUP_ORDER],
    groupHeader: (value, count, data) => {
      const h = data.filter((d) => d.verdict !== "drop").reduce((a, d) => a + pageHours(d), 0);
      return `<span style="font-family:var(--hed);font-size:16px;color:var(--navy)">${esc(groupL(value))}</span>` +
        `<span style="color:#7a748f;font-size:12px;margin-left:10px">${count} ${t("spr.pages")} · ${Math.round(h)}h</span>`;
    },
    columns: makeColumns(),
  });
  table.on("rowClick", (e, row) => openPanel(row.getData()));
  window.table = table;
  setTimeout(applyFilters, 60);
}

function applyFilters() {
  if (!window.table) return;
  const q = document.getElementById("f-search").value.toLowerCase();
  const f = { group: "f-group", status: "f-status", sprint: "f-sprint", verdict: "f-verdict", brand: "f-brand", category: "f-cat" };
  window.table.setFilter((d) => {
    if (q && !(d.title.toLowerCase().includes(q) || d.slug.toLowerCase().includes(q))) return false;
    for (const [field, id] of Object.entries(f)) { const v = document.getElementById(id).value; if (v !== "" && String(d[field]) !== String(v)) return false; }
    return true;
  });
  setTimeout(() => { document.getElementById("f-count").textContent = tf("f.showing", { a: window.table.getDataCount("active"), b: PAGES.length }); }, 50);
}

/* ── slide panel ─────────────────────────────────────────────────────────── */
const pagePlan = (d) => (PLANS && PLANS[d.slug]) ? PLANS[d.slug] : null;
let openPanelData = null;
const overlay = () => document.getElementById("overlay");
const panel = () => document.getElementById("panel");
function closePanel() { overlay().classList.remove("open"); panel().classList.remove("open"); openPanelData = null; }

function openPanel(d) {
  openPanelData = d;
  const ck = d.content_checklist;
  const ckHtml = Object.keys(ck).map((k) => `<div class="ck ${ck[k] ? "on" : ""}"><span class="box"></span>${k}</div>`).join("");
  const hrsRows = ROLES.map((r) => `<tr><td>${esc(roleL(r))}</td><td style="text-align:right">${d.role_hours[r] || 0}h</td></tr>`).join("");
  const plan = pagePlan(d);
  const buttons = [];
  if (d.url) buttons.push(`<a class="lk-btn" href="${esc(d.url)}" target="_blank" rel="noopener">${esc(t("p.see_old"))}</a>`);
  if (plan) buttons.push(`<button class="lk-btn plan" onclick="openPlanBySlug('${esc(d.slug)}')">${esc(t("p.open_plan"))}</button>`);
  const links = [];
  if (d.links && d.links.figma) links.push(`<a class="lk-btn ghost" href="${esc(d.links.figma)}" target="_blank" rel="noopener">Figma ↗</a>`);
  if (d.links && d.links.webflow) links.push(`<a class="lk-btn ghost" href="${esc(d.links.webflow)}" target="_blank" rel="noopener">Webflow ↗</a>`);
  const cons = d.consolidate_into ? `<div class="pb-sec"><h4>${esc(t("p.cons"))}</h4><code>/${esc(d.consolidate_into)}</code></div>` : "";
  panel().innerHTML = `
   <div class="panel-head">
     <button class="panel-close" onclick="closePanel()">×</button>
     <div style="display:flex;gap:6px;margin-bottom:8px">${badge("br-" + d.brand, d.brand.toUpperCase())} ${badge("vd-" + d.verdict, verdictL(d.verdict))} ${badge("st-" + d.status, statusL(d.status))}</div>
     <h3>${esc(d.title)}</h3>
   </div>
   <div class="panel-body">
     <div class="pb-sec">${buttons.join(" ")}</div>
     <div class="pb-sec"><h4>${esc(t("p.urls"))}</h4><div class="url-row"><code>${esc(d.url.replace("https://", ""))}</code><span class="arrow">→</span><code>${esc(d.new_path)}</code></div></div>
     <div class="pb-sec"><h4>${esc(t("p.meta"))}</h4><div style="font-size:13px">${esc(d.category)} · Sprint ${d.sprint} · ${esc(d.archetype)}</div></div>
     ${cons}
     <div class="pb-sec"><h4>${esc(t("p.checklist"))}</h4><div class="ck-grid">${ckHtml}</div></div>
     <div class="pb-sec"><h4>${esc(t("p.hours"))}</h4><table class="hrs-tbl">${hrsRows}<tr><td>${esc(t("p.total"))}</td><td style="text-align:right">${pageHours(d)}h</td></tr></table></div>
     ${d.notes ? `<div class="pb-sec"><h4>${esc(t("p.notes"))}</h4><div class="notes">${esc(d.notes)}</div></div>` : ""}
     ${links.length ? `<div class="pb-sec"><h4>${esc(t("p.links"))}</h4>${links.join("")}</div>` : ""}
     <div class="pb-sec"><h4>${esc(t("p.slug"))}</h4><code>${esc(d.slug)}</code></div>
   </div>`;
  overlay().classList.add("open"); panel().classList.add("open");
}

/* ── page-plan modal (mini admin dashboard) ──────────────────────────────── */
let openPlanData = null;
const modalOv = () => document.getElementById("modal-ov");
const modal = () => document.getElementById("modal");
function closePlan() { modalOv().classList.remove("open"); modal().classList.remove("open"); openPlanData = null; }
function openPlanBySlug(slug) { const p = PAGES.find((x) => x.slug === slug); if (p && pagePlan(p)) openPlan(p); }

const lsKey = (slug, id) => `sotsi_plan:${slug}:${id}`;
function secDone(slug, sec) { const v = localStorage.getItem(lsKey(slug, sec.id)); return v == null ? !!sec.done : v === "1"; }
function toggleSec(slug, id) {
  const p = PAGES.find((x) => x.slug === slug); const sec = pagePlan(p).sections.find((s) => s.id === id);
  const next = !secDone(slug, sec); localStorage.setItem(lsKey(slug, id), next ? "1" : "0");
  renderPlanBody(p); // re-render to refresh row + progress
}

function planProgress(slug, plan) {
  const secs = plan.sections.filter((s) => s.action !== "consolidar" && s.action !== "quitar");
  const done = secs.filter((s) => secDone(slug, s)).length;
  return { done, total: secs.length };
}

function openPlan(d) { openPlanData = d; renderPlanBody(d); modalOv().classList.add("open"); modal().classList.add("open"); }

function renderPlanBody(d) {
  const plan = pagePlan(d); const slug = d.slug;
  // header
  document.getElementById("modal-ey").textContent = t("pm.eyebrow");
  document.getElementById("modal-title").textContent = d.title;
  document.getElementById("modal-sub").textContent = (plan.base || "");
  // hour strip (role totals from the page object + grand total)
  const hours = ROLES.map((r) => `<div class="hour-card"><div class="hc-val">${d.role_hours[r] || 0}h</div><div class="hc-lab">${esc(roleL(r))}</div></div>`).join("");
  const total = `<div class="hour-card total"><div class="hc-val">${pageHours(d)}h</div><div class="hc-lab">${esc(t("p.total"))}</div></div>`;
  // ai context
  const ai = plan.ai_context;
  const aiHtml = ai ? `<div class="ai-card">
      <span class="ai-tag">✦ ${esc(t("pm.ai_tag"))}</span>
      <h3>${esc(t("pm.verdict"))}: <span class="ai-verdict">${esc(ai.verdict)}</span></h3>
      <p>${esc(ai.summary)}</p>
      <ul>${(ai.recommendations || []).map((r) => `<li>${esc(r)}</li>`).join("")}</ul>
    </div>` : "";
  // section table
  const prog = planProgress(slug, plan);
  const rows = plan.sections.map((s) => {
    const on = secDone(slug, s);
    return `<tr class="${on ? "is-done" : ""}">
      <td><div class="sec-name">${esc(s.section)}</div></td>
      <td class="skel old">${esc(s.old)}</td>
      <td class="skel">${esc(s.new)}</td>
      <td>${badge("ac-" + s.action, actionL(s.action))}</td>
      <td class="wf">${esc(s.webflow)}</td>
      <td class="pnote">${esc(s.notes || "")}</td>
      <td class="phrs">${s.hours ? s.hours + "h" : "—"}</td>
      <td style="text-align:center"><span class="plan-check ${on ? "on" : ""}" onclick="toggleSec('${esc(slug)}','${esc(s.id)}')">${on ? "✓" : ""}</span></td>
    </tr>`;
  }).join("");
  const table = `<div class="section-h">${esc(t("pm.sections"))}</div>
    <div class="plan-progress">${tf("pm.done_count", { a: prog.done, b: prog.total })} · <span style="color:var(--muted)">${esc(t("pm.note_local"))}</span></div>
    <div class="plan-tbl-wrap"><table class="plan-tbl"><thead><tr>
      <th>${esc(t("pm.col_section"))}</th><th>${esc(t("pm.col_old"))}</th><th>${esc(t("pm.col_new"))}</th>
      <th>${esc(t("pm.col_action"))}</th><th>${esc(t("pm.col_wf"))}</th><th>${esc(t("pm.col_notes"))}</th>
      <th style="text-align:right">${esc(t("pm.col_hrs"))}</th><th style="text-align:center">${esc(t("pm.col_done"))}</th>
    </tr></thead><tbody>${rows}</tbody></table></div>`;
  // template analysis
  const ta = plan.template_analysis;
  let taHtml = "";
  if (ta) {
    const gl = (ta.global_components || []).map((x) => `<li>${esc(x)}</li>`).join("");
    const bl = (ta.reusable_blocks || []).map((x) => `<span class="chip">${esc(x)}</span>`).join("");
    const st = (ta.strip_or_fix || []).map((x) => `<li>${esc(x)}</li>`).join("");
    taHtml = `<div class="section-h">${esc(ta.title || "Shimma")}</div>
      <div class="tpl-grid">
        <div class="tpl-card"><h4>${esc(t("pm.tpl_global"))}</h4><ul>${gl}</ul></div>
        <div class="tpl-card"><h4>${esc(t("pm.tpl_strip"))}</h4><ul>${st}</ul></div>
        <div class="tpl-card" style="grid-column:1/-1"><h4>${esc(t("pm.tpl_blocks"))}</h4><div class="chips">${bl}</div>
          <div class="tok-note"><b>${esc(t("pm.tpl_tokens"))}:</b> ${esc(ta.tokens || "")}</div></div>
      </div>`;
  }
  document.getElementById("modal-body").innerHTML =
    `<div class="hour-strip">${hours}${total}</div>${aiHtml}${table}${taHtml}`;
}

/* ── tabs + language toggle + boot ───────────────────────────────────────── */
function setLang(l) {
  LANG = l; localStorage.setItem("sotsi_lang", l);
  const m = computeMeta();
  applyI18n(); renderKpis(m); renderBars(m); renderSprints(); renderGroups(); renderPlansList(); renderGuide(); populateFilters();
  if (window.table) buildTable();
  if (openPanelData) openPanel(openPanelData);
  if (openPlanData) renderPlanBody(openPlanData);
}

function initTabs() {
  document.querySelectorAll(".tab-btn").forEach((b) => b.onclick = () => {
    document.querySelectorAll(".tab-btn").forEach((x) => x.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach((x) => x.classList.remove("active"));
    b.classList.add("active");
    document.getElementById("tab-" + b.dataset.tab).classList.add("active");
    if (b.dataset.tab === "board") { if (!window.table) buildTable(); else setTimeout(() => window.table.redraw(true), 30); }
  });
}

function boot() {
  const m = computeMeta();
  applyI18n();
  renderKpis(m); renderBars(m); renderSprints(); renderGroups(); renderPlansList(); renderGuide(); populateFilters();
  initTabs();
  document.querySelectorAll(".lang-toggle button").forEach((b) => b.onclick = () => setLang(b.dataset.lang));
  ["f-search", "f-group", "f-status", "f-sprint", "f-verdict", "f-brand", "f-cat"].forEach((id) => {
    document.getElementById(id).addEventListener(id === "f-search" ? "input" : "change", applyFilters);
  });
  document.getElementById("f-clear").onclick = () => {
    ["f-search", "f-status", "f-sprint", "f-verdict", "f-brand", "f-cat", "f-group"].forEach((id) => document.getElementById(id).value = "");
    applyFilters();
  };
  overlay().onclick = closePanel;
  modalOv().onclick = closePlan;
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") { if (openPlanData) closePlan(); else closePanel(); } });
}
document.addEventListener("DOMContentLoaded", boot);
