(() => {
// "Write a note": GitHub new-file page with filename = username and a starter template
const w = document.getElementById("write");
if (w) {
  const input = document.getElementById("ghUser"), btn = document.getElementById("writeBtn");
  const TEMPLATE = "## In one sentence\n\n\n## What the paper does\n\n\n## My take\n\n\n## Questions\n\n";
  const ok = s => /^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$/.test(s);
  const base = `https://github.com/${w.dataset.repo}`;
  try { input.value = localStorage.getItem("ghUser") || ""; } catch (e) {}
  function update(){
    const u = input.value.trim().replace(/^@/, "");
    if (!ok(u)) { btn.setAttribute("aria-disabled", "true"); btn.textContent = "Write a note"; return; }
    btn.removeAttribute("aria-disabled");
    try { localStorage.setItem("ghUser", u); } catch (e) {}
    if (document.getElementById("n-" + u)) {
      btn.textContent = "Edit your note";
      btn.href = `${base}/edit/${w.dataset.branch}/${w.dataset.dir}/${encodeURIComponent(u)}.md`;
    } else {
      btn.textContent = "Write a note";
      btn.href = `${base}/new/${w.dataset.branch}/${w.dataset.dir}?filename=${encodeURIComponent(u + ".md")}&value=${encodeURIComponent(TEMPLATE)}`;
    }
  }
  input.addEventListener("input", update);
  update();
}

// math
if (window.katex) document.querySelectorAll(".md .math").forEach(el => {
  try { katex.render(el.textContent, el, {displayMode: el.classList.contains("block"), throwOnError: false}); } catch (e) {}
});
})();
