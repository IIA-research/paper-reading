(() => {
const $ = id => document.getElementById(id);
const DATA = JSON.parse($("data").textContent);
const SECS = JSON.parse($("secs").textContent);           // [{k, c, code, d}]
const SEC = Object.fromEntries(SECS.map(s => [s.k, s]));
const SEC_I = Object.fromEntries(SECS.map((s, i) => [s.k, i]));
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const PAGE = 80;

// ---- facets: OR within a facet, AND across facets ----
const venueKind = d => d.v === "arXiv" ? "arXiv preprint" : (!d.v || d.v === "Unknown") ? "Unknown" : "Peer-reviewed";
const EARLY = "2019 and earlier";
const yearBin = d => d.y >= 2020 ? String(d.y) : EARLY;
const FACETS = [
  {k: "s",  name: "Section",            get: d => state.also ? [d.s, ...d.al] : [d.s], order: SECS.map(s => s.k)},
  {k: "ft", name: "Featured",           get: d => [d.f ? "Featured" : "Not featured"], order: ["Featured", "Not featured"]},
  {k: "ty", name: "Paper type",         get: d => [d.ty]},
  {k: "u",  name: "Who plays the user", get: d => [d.u]},
  {k: "tr", name: "Training",           get: d => [d.tr]},
  {k: "ml", name: "Model",              get: d => [d.ml]},
  {k: "mo", name: "Modality",           get: d => d.mo},
  {k: "y",  name: "Year",               get: d => [yearBin(d)], sortBy: "value"},
  {k: "pv", name: "Venue",              get: d => [venueKind(d)]},
  {k: "nt", name: "Notes",              get: d => [d.a.length ? "Has notes" : "No notes yet"]},
  {k: "by", name: "Note author",        get: d => d.a},
];
const FK = Object.fromEntries(FACETS.map(f => [f.k, f]));

const state = {q: "", sort: "new", also: false, mv: "time", mc: "u", sel: Object.fromEntries(FACETS.map(f => [f.k, new Set()]))};
let shown = PAGE;

// ---- URL hash <-> state, so a filtered view can be shared ----
function readHash(){
  const h = new URLSearchParams(location.hash.slice(1));
  FACETS.forEach(f => { state.sel[f.k] = new Set((h.get(f.k) || "").split("|").filter(Boolean)); });
  state.also = h.get("also") === "1";
  state.sort = h.get("sort") || "new";
  state.q = h.get("q") || "";
  state.mv = h.get("mv") || "time"; state.mc = h.get("mc") || "u";
  $("q").value = state.q; $("fSort").value = state.sort;
}
function writeHash(){
  const h = new URLSearchParams();
  FACETS.forEach(f => { if (state.sel[f.k].size) h.set(f.k, [...state.sel[f.k]].join("|")); });
  if (state.also) h.set("also", "1");
  if (state.sort !== "new") h.set("sort", state.sort);
  if (state.q) h.set("q", state.q);
  if (state.mv !== "time") h.set("mv", state.mv);
  if (state.mc !== "u") h.set("mc", state.mc);
  const s = h.toString();
  history.replaceState(null, "", s ? "#" + s : location.pathname + location.search);
}

const matchesQ = d => !state.q || [d.t, d.m, d.tp, d.v, d.a.join(" ")].join(" ").toLowerCase().includes(state.q.toLowerCase());
const passes = (d, skip) => matchesQ(d) && FACETS.every(f => f.k === skip || !state.sel[f.k].size || f.get(d).some(v => state.sel[f.k].has(v)));

// ---- build the facet panel once; later renders only update counts ----
function optionsOf(f){
  const all = new Map();
  DATA.forEach(d => (f.k === "s" ? [d.s, ...d.al] : f.get(d)).forEach(v => { if (v) all.set(v, (all.get(v) || 0) + 1); }));
  let opts = [...all.keys()];
  if (f.order) opts = f.order.filter(v => all.has(v)).concat(opts.filter(v => !f.order.includes(v)));
  else if (f.sortBy === "value") opts.sort((a, b) => b.localeCompare(a));
  else opts.sort((a, b) => all.get(b) - all.get(a) || a.localeCompare(b));
  return opts;
}
function buildFacets(){
  $("facetBody").innerHTML = FACETS.map(f => {
    const opts = optionsOf(f);
    if (!opts.length) return "";
    const many = opts.length > 7;
    return `<fieldset class="fg${many ? " long" : ""}" data-k="${f.k}"><legend>${esc(f.name)}</legend>
      ${opts.map((v, i) => `<label class="opt${i >= 6 && many ? " extra" : ""}">
        <input type="checkbox" data-k="${f.k}" value="${esc(v)}">
        ${f.k === "s" ? `<span class="sw c-${esc((SEC[v] || {}).c || "gray")}"></span>` : ""}
        <span class="ol">${esc(v)}</span><span class="oc"></span></label>`).join("")}
      ${many ? `<button class="link fmore" type="button">Show all ${opts.length}</button>` : ""}
      ${f.k === "s" ? `<label class="opt sub"><input type="checkbox" id="alsoT"><span class="ol">Also count papers that touch a section</span></label>` : ""}
    </fieldset>`;
  }).join("");
}
function updateFacets(){
  FACETS.forEach(f => {
    const pool = DATA.filter(d => passes(d, f.k)), counts = new Map();
    pool.forEach(d => f.get(d).forEach(v => counts.set(v, (counts.get(v) || 0) + 1)));
    document.querySelectorAll(`.opt input[data-k="${f.k}"]`).forEach(inp => {
      const n = counts.get(inp.value) || 0, on = state.sel[f.k].has(inp.value);
      inp.checked = on;
      const lab = inp.closest(".opt");
      lab.querySelector(".oc").textContent = n;
      lab.classList.toggle("zero", !n && !on);
      lab.classList.toggle("on", on);
    });
  });
  const a = $("alsoT"); if (a) a.checked = state.also;
}

// ---- dot map: one dot per paper, rows by year or by section ----
// Section hues belong to sections only, so other attributes are shown with black/grey fills and rings.
const ATTR = {
  u:  {name: "Who plays the user", get: d => d.u === "Unspecified" ? "None" : d.u, order: ["Human", "User simulator", "Static dataset", "None"]},
  tr: {name: "Training", get: d => d.tr, order: ["RL", "SFT", "Preference optimization", "Training-free", "Not applicable"]},
  ty: {name: "Paper type", get: d => d.ty, order: ["Method", "Benchmark", "Analysis", "User study", "Survey / position"]},
  ml: {name: "Model", get: d => d.ml, order: ["LLM", "VLM", "Embodied / VLA", "Speech", "None"]},
};
const SHADES = ["k0", "k1", "k2", "k3", "k4"];   // solid black, grey, black ring, grey ring, light grey
const THIS_YEAR = new Date().getFullYear();
const mapColor = () => state.mc in ATTR || state.mc === "s" ? state.mc : "u";
function dotClass(d){
  const mc = mapColor();
  if (mc === "s") return "c-" + ((SEC[d.s] || {}).c || "gray") + " ink";
  const A = ATTR[mc], i = A.order.indexOf(A.get(d));
  return SHADES[i < 0 ? 4 : i];
}
function renderMap(){
  const mc = mapColor(), mv = state.mv === "section" ? "section" : "time";
  document.querySelectorAll("#map .seg button").forEach(b => b.setAttribute("aria-pressed", b.dataset.mv === mv));
  $("mapColor").value = mc;
  const keep = new Set(DATA.filter(d => passes(d)).map(d => d.slug));
  // rows
  let rows;
  if (mv === "time") {
    const ys = [...new Set(DATA.map(d => d.y).filter(y => y && y <= THIS_YEAR))].sort((a, b) => b - a);
    const recent = ys.filter(y => y >= 2020), early = ys.filter(y => y < 2020);
    rows = recent.map(y => ({key: String(y), label: `<span class="yr">${y}</span>`, papers: DATA.filter(d => d.y === y), fk: "y", fv: String(y)}));
    if (early.length) rows.push({key: EARLY, label: `<span class="yr">≤2019</span>`, papers: DATA.filter(d => d.y < 2020), fk: "y", fv: EARLY});
  } else {
    rows = SECS.map(s => ({key: s.k, label: `<span class="code c-${esc(s.c)}">${esc(s.code)}</span><span class="sn">${esc(s.k)}</span>`, papers: DATA.filter(d => d.s === s.k), fk: "s", fv: s.k}));
  }
  const order = mc === "s" ? (d => SEC_I[d.s] ?? 99) : (d => { const i = ATTR[mc].order.indexOf(ATTR[mc].get(d)); return i < 0 ? 99 : i; });
  $("mrows").innerHTML = rows.map(r => {
    const ps = [...r.papers].sort((a, b) => order(a) - order(b) || (b.y || 0) - (a.y || 0));
    const n = ps.filter(d => keep.has(d.slug)).length, on = state.sel[r.fk].has(r.fv);
    return `<div class="mrow${on ? " on" : ""}">
      <button class="mlab" data-fk="${r.fk}" data-fv="${esc(r.fv)}" aria-pressed="${on}">${r.label}</button>
      <div class="mdots">${ps.map(d => `<i class="pt ${dotClass(d)}${keep.has(d.slug) ? "" : " off"}${d.a.length ? " nt" : ""}${d.f ? " fx" : ""}" data-slug="${esc(d.slug)}"></i>`).join("")}</div>
      <span class="mct">${n === ps.length ? ps.length : `${n}<span>/${ps.length}</span>`}</span>
    </div>`;
  }).join("");
  // legend
  if (mc === "s") {
    $("mlegend").innerHTML = SECS.map(s => `<span><i class="pt c-${esc(s.c)} ink"></i>${esc(s.k)}</span>`).join("");
  } else {
    const A = ATTR[mc], cnt = {};
    DATA.filter(d => keep.has(d.slug)).forEach(d => { const v = A.get(d); cnt[v] = (cnt[v] || 0) + 1; });
    $("mlegend").innerHTML = A.order.map((v, i) => `<span><i class="pt ${SHADES[i]}"></i>${esc(v)} <b>${cnt[v] || 0}</b></span>`).join("");
  }
}
// "EMNLP 2026 Findings" already names the year; "arXiv" does not
const venueLabel = d => !d.v || d.v === "Unknown" ? String(d.y || "") : String(d.v).includes(String(d.y)) ? d.v : `${d.v} ${d.y}`;
const BY_SLUG = Object.fromEntries(DATA.map(d => [d.slug, d]));
function showMapTip(el){
  const d = BY_SLUG[el.dataset.slug]; if (!d) return;
  const s = SEC[d.s] || {c: "gray", code: "··"}, mc = mapColor();
  const tip = $("mtip");
  tip.innerHTML = `<div class="tt">${esc(d.t)}</div>
    <div class="tm"><span class="code c-${esc(s.c)}">${esc(s.code)}</span>${esc(d.s)} · ${esc(d.y)}${mc !== "s" ? ` · ${esc(ATTR[mc].get(d))}` : ""}${d.a.length ? ` · ${d.a.length} note${d.a.length === 1 ? "" : "s"}` : ""}</div>`;
  tip.hidden = false;
  const box = $("map").getBoundingClientRect(), r = el.getBoundingClientRect();
  tip.style.left = Math.min(Math.max(r.left - box.left - 20, 0), box.width - tip.offsetWidth) + "px";
  tip.style.top = (r.bottom - box.top + 8) + "px";
}

// ---- sorting ----
const SORTS = {
  featured: (a, b) => b.f - a.f || a.fr - b.fr || (b.y || 0) - (a.y || 0),
  new: (a, b) => (b.y || 0) - (a.y || 0) || a.t.localeCompare(b.t),
  old: (a, b) => (a.y || 0) - (b.y || 0) || a.t.localeCompare(b.t),
  title: (a, b) => a.t.localeCompare(b.t),
  noted: (a, b) => (b.last || "").localeCompare(a.last || "") || (b.y || 0) - (a.y || 0),
  notes: (a, b) => b.a.length - a.a.length || (b.last || "").localeCompare(a.last || ""),
  section: (a, b) => (SEC_I[a.s] ?? 99) - (SEC_I[b.s] ?? 99) || (b.y || 0) - (a.y || 0),
};

function render(){
  // section bar mirrors the Section facet
  const ss = state.sel.s;
  $("secbar").classList.toggle("has-on", ss.size > 0);
  document.querySelectorAll(".blk").forEach(b => { const on = ss.has(b.dataset.s); b.classList.toggle("on", on); b.setAttribute("aria-pressed", on); });

  updateFacets();
  renderMap();

  // active filter chips
  const chips = [];
  FACETS.forEach(f => state.sel[f.k].forEach(v => chips.push(
    `<button class="act" data-k="${f.k}" value="${esc(v)}">${f.k === "s" ? `<span class="sw c-${esc((SEC[v] || {}).c || "gray")}"></span>` : `<span class="fn">${esc(f.name)}:</span>`}${esc(v)} ×</button>`)));
  if (state.q) chips.push(`<button class="act" data-q="1"><span class="fn">Search:</span>${esc(state.q)} ×</button>`);
  $("active").innerHTML = chips.join("");
  const nsel = FACETS.reduce((n, f) => n + state.sel[f.k].size, 0);
  $("clearAll").hidden = !nsel && !state.q;
  $("fcount").textContent = nsel ? ` (${nsel})` : "";

  const r = DATA.filter(d => passes(d)).sort(SORTS[state.sort] || SORTS.new);
  $("count").textContent = `${r.length} of ${DATA.length}`;
  const byYear = state.sort === "new" || state.sort === "old", ycount = {};
  if (byYear) r.forEach(d => { ycount[d.y] = (ycount[d.y] || 0) + 1; });
  let lastY = null;
  $("list").innerHTML = r.length ? r.slice(0, shown).map(d => {
    const s = SEC[d.s] || {c: "gray", code: "··"};
    let head = "";
    if (byYear && d.y !== lastY) { lastY = d.y; head = `<div class="yh"><span>${esc(d.y)}</span><span class="mono">${ycount[d.y]} paper${ycount[d.y] === 1 ? "" : "s"}</span></div>`; }
    return head + `<a class="row c-${esc(s.c)}" href="p/${encodeURIComponent(d.slug)}/index.html">
      <span class="code" title="${esc(d.s)}">${esc(s.code)}</span>
      <span class="mid"><span class="t">${esc(d.t)}</span>
        <span class="meta">${d.f ? `<span class="fe">★ Featured</span>` : ""}<span class="ty">${esc(d.ty)}</span><span class="vn">${esc(venueLabel(d))}</span>${d.a.length ? `<span class="nn">${d.a.length} note${d.a.length === 1 ? "" : "s"}</span>` : ""}</span>
        ${d.m ? `<span class="s">${esc(d.m)}</span>` : ""}</span>
      ${d.th ? `<img class="th" src="thumbs/${encodeURIComponent(d.slug)}.webp" alt="" loading="lazy" width="84" height="109">` : ""}
    </a>`;
  }).join("") : `<p class="empty">No papers match. Try removing a filter.</p>`;
  $("more").hidden = r.length <= shown;
  $("more").textContent = `More (${r.length - shown})`;
}

// ---- hover card on the section bar ----
const pop = $("secpop");
let popT;
function showPop(b){
  clearTimeout(popT);
  const s = SEC[b.dataset.s]; if (!s) return;
  const mine = DATA.filter(d => d.s === s.k), types = new Map(), users = new Map();
  mine.forEach(d => { types.set(d.ty, (types.get(d.ty) || 0) + 1); users.set(d.u, (users.get(d.u) || 0) + 1); });
  const top = m => [...m].filter(([k]) => k).sort((a, b) => b[1] - a[1]).slice(0, 4).map(([k, n]) => `${esc(k)} <b>${n}</b>`).join(" · ");
  const recent = mine.filter(d => d.a.length).sort(SORTS.noted)[0];
  pop.className = "secpop c-" + s.c;
  pop.innerHTML = `<div class="ph"><span class="sw"></span><b>${esc(s.k)}</b><span class="mono">${s.n} papers · ${s.done} with notes</span></div>
    <p>${esc(s.d)}</p>
    <dl>
      <dt>Owner</dt><dd>${s.o.length ? s.o.map(esc).join(", ") : "Unclaimed"}</dd>
      <dt>Types</dt><dd>${top(types)}</dd>
      <dt>User</dt><dd>${top(users)}</dd>
      ${recent ? `<dt>Latest note</dt><dd>${esc(recent.a[0])} on ${esc(recent.t)}</dd>` : ""}
    </dl>
    <div class="hint">${state.sel.s.has(s.k) ? "Click to remove this filter" : "Click to filter"}</div>`;
  pop.hidden = false;
  // place under the block, kept inside the bar's width
  const wrap = pop.parentElement.getBoundingClientRect(), r = b.getBoundingClientRect();
  const w = pop.offsetWidth, x = Math.min(Math.max(r.left - wrap.left + r.width / 2 - w / 2, 0), wrap.width - w);
  pop.style.left = x + "px";
  pop.style.top = (r.bottom - wrap.top + 8) + "px";
}
function hidePop(){ popT = setTimeout(() => { pop.hidden = true; }, 80); }
document.querySelectorAll(".seg.blk").forEach(b => {
  b.addEventListener("mouseenter", () => showPop(b));
  b.addEventListener("focus", () => showPop(b));
  b.addEventListener("mouseleave", hidePop);
  b.addEventListener("blur", hidePop);
});
document.addEventListener("keydown", e => { if (e.key === "Escape") pop.hidden = true; });

function changed(){ shown = PAGE; writeHash(); render(); }
function toggle(k, v){ const s = state.sel[k]; s.has(v) ? s.delete(v) : s.add(v); changed(); }

buildFacets();
$("facetBody").addEventListener("change", e => {
  const t = e.target;
  if (t.id === "alsoT") { state.also = t.checked; return changed(); }
  if (t.dataset.k) toggle(t.dataset.k, t.value);
});
$("facetBody").addEventListener("click", e => {
  const m = e.target.closest(".fmore"); if (!m) return;
  const fg = m.closest(".fg"); fg.classList.toggle("open");
  m.textContent = fg.classList.contains("open") ? "Show fewer" : `Show all ${fg.querySelectorAll(".opt:not(.sub)").length}`;
});
$("active").addEventListener("click", e => {
  const b = e.target.closest(".act"); if (!b) return;
  if (b.dataset.q) { state.q = ""; $("q").value = ""; return changed(); }
  toggle(b.dataset.k, b.value);
});
$("clearAll").addEventListener("click", () => { FACETS.forEach(f => state.sel[f.k].clear()); state.q = ""; $("q").value = ""; changed(); });
$("secbar").addEventListener("click", e => { const b = e.target.closest(".blk"); if (b) { toggle("s", b.dataset.s); if (b.classList.contains("seg")) showPop(b); } });
let qt; $("q").addEventListener("input", () => { clearTimeout(qt); qt = setTimeout(() => { state.q = $("q").value.trim(); changed(); }, 150); });
$("fSort").addEventListener("change", () => { state.sort = $("fSort").value; changed(); });
$("more").addEventListener("click", () => { shown += PAGE; render(); });
document.querySelector("#map .seg").addEventListener("click", e => { const b = e.target.closest("[data-mv]"); if (b) { state.mv = b.dataset.mv; writeHash(); renderMap(); } });
$("mapColor").addEventListener("change", () => { state.mc = $("mapColor").value; writeHash(); renderMap(); });
$("mrows").addEventListener("click", e => {
  const lab = e.target.closest(".mlab"); if (lab) return toggle(lab.dataset.fk, lab.dataset.fv);
  const pt = e.target.closest(".pt"); if (pt) location.href = "p/" + encodeURIComponent(pt.dataset.slug) + "/index.html";
});
$("mrows").addEventListener("mouseover", e => { const pt = e.target.closest(".pt"); if (pt) showMapTip(pt); });
$("mrows").addEventListener("mouseleave", () => { $("mtip").hidden = true; });
$("ftoggle").addEventListener("click", () => {
  const open = $("facets").classList.toggle("open");
  $("ftoggle").setAttribute("aria-expanded", open);
});
document.querySelector(".feat-all")?.addEventListener("click", () => setTimeout(() => document.querySelector(".results")?.scrollIntoView({behavior: "smooth"}), 0));
window.addEventListener("hashchange", () => { readHash(); shown = PAGE; render(); });
readHash();
render();
})();
