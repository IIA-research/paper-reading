(() => {
// "Write a note": GitHub new-file page with filename = username and a starter template
const w = document.getElementById("write");
if (w) {
  const input = document.getElementById("ghUser"), nick = document.getElementById("nick"), btn = document.getElementById("writeBtn");
  const BODY = "## In one sentence\n\n\n## What the paper does\n\n\n## My take\n\n\n## Questions\n\n";
  // front matter carries the nickname; JSON quoting keeps it valid YAML whatever it contains
  const template = name => `---\nname: ${JSON.stringify(name)}\n---\n\n${BODY}`;
  const ok = s => /^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$/.test(s);
  const base = `https://github.com/${w.dataset.repo}`;
  try { input.value = localStorage.getItem("ghUser") || ""; nick.value = localStorage.getItem("nick") || ""; } catch (e) {}
  function update(){
    const u = input.value.trim().replace(/^@/, ""), n = nick.value.trim();
    const mine = ok(u) && document.getElementById("n-" + u);
    if (!ok(u) || (!n && !mine)) { btn.setAttribute("aria-disabled", "true"); btn.textContent = "Write a note"; return; }
    btn.removeAttribute("aria-disabled");
    try { localStorage.setItem("ghUser", u); localStorage.setItem("nick", n); } catch (e) {}
    if (document.getElementById("n-" + u)) {
      btn.textContent = "Edit your note";
      btn.href = `${base}/edit/${w.dataset.branch}/${w.dataset.dir}/${encodeURIComponent(u)}.md`;
    } else {
      btn.textContent = "Write a note";
      btn.href = `${base}/new/${w.dataset.branch}/${w.dataset.dir}?filename=${encodeURIComponent(u + ".md")}&value=${encodeURIComponent(template(n))}`;
    }
  }
  input.addEventListener("input", update);
  nick.addEventListener("input", update);
  update();
}

// math
if (window.katex) document.querySelectorAll(".md .math").forEach(el => {
  try { katex.render(el.textContent, el, {displayMode: el.classList.contains("block"), throwOnError: false}); } catch (e) {}
});
})();
