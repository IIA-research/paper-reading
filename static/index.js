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
const EARLY = "2021 and earlier";
const yearBin = d => d.y >= 2022 ? String(d.y) : EARLY;
// Papers are told apart by venue, year and kind. The old sections stay in the data but are not shown.
const STATUS = {published: "Accepted", accepted: "Accepted", workshop: "Workshop", preprint: "arXiv only"};
const FACETS = [
  {k: "ac", name: "Accepted?", get: d => [STATUS[d.st] || "arXiv only"], order: ["Accepted", "Workshop", "arXiv only"]},
  {k: "va", name: "Venue",     get: d => STATUS[d.st] === "Accepted" ? [d.va] : []},
  {k: "y",  name: "Year",      get: d => [yearBin(d)], sortBy: "value"},
  {k: "kd", name: "Type",      get: d => [d.k], order: ["Paper", "Benchmark"]},
  {k: "ft", name: "Featured",  get: d => [d.f ? "Featured" : "Not featured"], order: ["Featured", "Not featured"]},
  {k: "nt", name: "Notes",     get: d => [d.a.length ? "Has notes" : "No notes yet"]},
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

const matchesQ = d => !state.q || [d.t, d.m, d.tp, d.v, d.a.join(" "), (d.an || []).join(" ")].join(" ").toLowerCase().includes(state.q.toLowerCase());
const passes = (d, skip) => { const sk = [].concat(skip ?? []); return matchesQ(d) && FACETS.every(f => sk.includes(f.k) || !state.sel[f.k].size || f.get(d).some(v => state.sel[f.k].has(v))); };

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

// "EMNLP 2026 Findings" already names the year; "arXiv" does not
const venueLabel = d => !d.v || d.v === "Unknown" ? String(d.y || "") : String(d.v).includes(String(d.y)) ? d.v : `${d.v} ${d.y}`;

const venueBadge = d => d.st === "preprint" ? `<span class="vb pp">${esc(d.ax)}</span>`
  : `<span class="vb${d.st === "workshop" ? " ws" : ""}">${esc(d.v)}</span>`;

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
  updateFacets();
  $("featOnly").setAttribute("aria-pressed", state.sel.ft.has("Featured"));
  $("accOnly").setAttribute("aria-pressed", state.sel.ac.has("Accepted"));

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
    return head + `<a class="row" href="p/${encodeURIComponent(d.slug)}/index.html">
      <span class="mid"><span class="t">${esc(d.t)}</span>
        <span class="meta">${venueBadge(d)}${d.k === "Benchmark" ? `<span class="bm">Benchmark</span>` : ""}${d.f ? `<span class="fe">★ Featured</span>` : ""}${d.a.length ? `<span class="nn">${d.a.length} note${d.a.length === 1 ? "" : "s"}</span>` : ""}</span>
        ${d.m ? `<span class="s">${esc(d.m)}</span>` : ""}</span>
      ${d.fg ? `<img class="th fig" src="figs/${encodeURIComponent(d.slug)}.webp" alt="" loading="lazy">` : d.th ? `<img class="th" src="thumbs/${encodeURIComponent(d.slug)}.webp" alt="" loading="lazy" width="84" height="109">` : ""}
    </a>`;
  }).join("") : `<p class="empty">No papers match. Try removing a filter.</p>`;
  $("more").hidden = r.length <= shown;
  $("more").textContent = `More (${r.length - shown})`;
}

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
$("featOnly").addEventListener("click", () => toggle("ft", "Featured"));
$("accOnly").addEventListener("click", () => toggle("ac", "Accepted"));
let qt; $("q").addEventListener("input", () => { clearTimeout(qt); qt = setTimeout(() => { state.q = $("q").value.trim(); changed(); }, 150); });
$("fSort").addEventListener("change", () => { state.sort = $("fSort").value; changed(); });
$("more").addEventListener("click", () => { shown += PAGE; render(); });
$("ftoggle").addEventListener("click", () => {
  const open = $("facets").classList.toggle("open");
  $("ftoggle").setAttribute("aria-expanded", open);
});
window.addEventListener("hashchange", () => { readHash(); shown = PAGE; render(); });
readHash();
render();
})();
