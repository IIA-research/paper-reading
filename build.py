"""Build the site: read site.yaml, papers.yaml and notes/, write to _site/.

    python build.py                          # build
    python -m http.server -d _site 8000      # preview at http://localhost:8000
"""
import collections
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
import datetime as dt
import json
import pathlib
import re
import shutil
import subprocess
import sys

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markdown_it import MarkdownIt
from mdit_py_plugins.dollarmath import dollarmath_plugin

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT / "_site"
NOTES = ROOT / "notes"
GH_USER = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$")

# Notes are untrusted input: raw HTML is disabled and javascript: links are rejected.
MD = (
    MarkdownIt("commonmark", {"html": False})
    .enable(["table", "strikethrough"])
    .use(dollarmath_plugin)
)

errors, warnings = [], []


def slugify(pid):
    return re.sub(r"[^A-Za-z0-9._-]+", "-", str(pid)).strip("-") or "paper"


def load_yaml(name):
    path = ROOT / name
    if not path.exists():
        sys.exit(f"Missing {name}")
    return yaml.safe_load(path.read_text(encoding="utf8")) or {}


def git_dates():
    """Last commit date of each file under notes/ (empty when not in a git repo)."""
    try:
        out = subprocess.run(
            ["git", "-c", "core.quotepath=false", "log", "--format=__%cs", "--name-only", "--", "notes"],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return {}
    dates, cur = {}, None
    for line in out.splitlines():
        if line.startswith("__"):
            cur = line[2:]
        elif line.strip() and cur:
            dates.setdefault(line.strip(), cur)  # log is newest first; keep the newest
    return dates


def main():
    site = load_yaml("site.yaml")
    papers = load_yaml("papers.yaml") or []
    repo = site.get("repo", "")
    branch = site.get("branch", "main")
    sections = site.get("sections") or []
    sec_by_key = {s["key"]: s for s in sections}
    for s in sections:
        s["owners"] = [o for o in (s.get("owners") or []) if o]
        s.setdefault("color", "gray")
        s.setdefault("code", s["key"][:2])

    by_slug = {}
    for p in papers:
        if not p.get("id") or not p.get("title"):
            errors.append(f"papers.yaml: entry without id or title: {p}")
            continue
        p["slug"] = slugify(p["id"])
        # titles with inline math: "$τ$-Bench" -> "τ-Bench", "$\\neq$" -> "≠"
        t = str(p["title"]).replace("$\\neq$", "≠").replace("$^2$", "²")
        p["title"] = re.sub(r"\$([^$]+)\$", r"\1", t)
        if p["slug"] in by_slug:
            errors.append(f"papers.yaml: duplicate id {p['id']}")
            continue
        if p.get("section") not in sec_by_key:
            warnings.append(f"{p['id']}: section '{p.get('section')}' is not in site.yaml")
        p["notes"] = []
        p["thumb"] = (ROOT / "thumbs" / f"{p['slug']}.webp").exists()
        p["featured"] = None
        # option one: papers are told apart by venue, year and kind (Benchmark vs Paper)
        p["kind"] = "Benchmark" if p.get("type") == "Benchmark" else "Paper"
        st = p.get("status") or "preprint"
        p["venue_group"] = (re.sub(r"\s*(?:19|20)\d{2}.*$", "", p.get("venue") or "").strip() or p.get("venue")) if st in ("published", "accepted") \
            else ("Workshop" if st == "workshop" else "arXiv only")
        # arXiv ids are YYMM.NNNNN, so the first-version month is in the id (or the arxiv.org URL)
        m = re.search(r"(?<![\d.])(\d{2})(0[1-9]|1[0-2])\.\d{4,5}", f"{p['id']} {p.get('url') or ''}")
        p["arxiv_label"] = f"arXiv {MONTHS[int(m.group(2)) - 1]} 20{m.group(1)}" if m else f"arXiv {p.get('year') or ''}".strip()
        by_slug[p["slug"]] = p

    # Notes: notes/<paper slug>/<GitHub username>.md
    dates = git_dates()
    for f in sorted(NOTES.glob("*/*.md")) if NOTES.exists() else []:
        if f.name.startswith(("_", ".")) or f.stem.upper() == "README":
            continue
        slug, author = f.parent.name, f.stem
        paper = by_slug.get(slug)
        if not paper:
            warnings.append(f"{f.relative_to(ROOT)}: no paper with id {slug} in papers.yaml, skipped")
            continue
        if not GH_USER.match(author):
            warnings.append(f"{f.relative_to(ROOT)}: file name must be a GitHub username, skipped")
            continue
        text = f.read_text(encoding="utf8").strip()
        if not text:
            continue
        rel = f.relative_to(ROOT).as_posix()
        date = dates.get(rel) or dt.date.fromtimestamp(f.stat().st_mtime).isoformat()
        paper["notes"].append({
            "author": author,
            "html": MD.render(text),
            "date": date,
            "path": rel,
        })
    for p in by_slug.values():
        p["notes"].sort(key=lambda n: n["date"], reverse=True)
        p["last"] = p["notes"][0]["date"] if p["notes"] else ""

    if errors:
        print("\n".join("Error: " + e for e in errors))
        sys.exit(1)

    # stats
    plist = list(by_slug.values())
    for s in sections:
        mine = [p for p in plist if p.get("section") == s["key"]]
        s["n"] = len(mine)
        s["done"] = sum(1 for p in mine if p["notes"])
    all_notes = [(n, p) for p in plist for n in p["notes"]]
    # featured.yaml: admins' picks, in display order. BaseLoader keeps ids as text (2610.10740 must not become a float).
    picks = []
    fpath = ROOT / "featured.yaml"
    if fpath.exists():
        by_id = {str(p["id"]): p for p in plist}
        for rank, f in enumerate(yaml.load(fpath.read_text(encoding="utf8"), Loader=yaml.BaseLoader) or []):
            fid = (f.get("id") if isinstance(f, dict) else f) or ""
            p = by_id.get(str(fid).strip())
            if not p:
                warnings.append(f"featured.yaml: no paper with id {fid}")
                continue
            p["featured"] = {"why": (f.get("why") or "").strip() if isinstance(f, dict) else "",
                             "by": (f.get("by") or "").strip() if isinstance(f, dict) else "", "rank": rank}
            picks.append(p)
    recent = sorted(all_notes, key=lambda x: x[0]["date"], reverse=True)[:8]
    vstat = collections.Counter(p.get("status") or "preprint" for p in plist)
    stats = {
        "accepted": vstat["published"] + vstat["accepted"], "workshop": vstat["workshop"], "preprint": vstat["preprint"],
        "papers": len(plist),
        "with_notes": sum(1 for p in plist if p["notes"]),
        "notes": len(all_notes),
        "people": len({n["author"] for n, _ in all_notes} | {o for s in sections for o in s["owners"]}),
    }

    gc = site.get("giscus") or {}
    giscus = None
    if gc.get("repo_id") and gc.get("category_id"):
        giscus = {"repo": repo, **gc}

    # "How methods are shifting": share of papers per attribute value, earlier years vs the last two years
    this_year = dt.date.today().year
    recent_ps = [p for p in plist if str(p.get("year") or "").isdigit() and this_year - 1 <= int(p["year"]) <= this_year]
    early_ps = [p for p in plist if str(p.get("year") or "").isdigit() and int(p["year"]) < this_year - 1]
    attr_defs = [
        ("u", "Who plays the user", lambda p: "None" if p.get("user") == "Unspecified" else p.get("user"), ["Human", "User simulator", "Static dataset", "None"]),
        ("tr", "Training", lambda p: p.get("training"), ["RL", "SFT", "Preference optimization", "Training-free", "Not applicable"]),
        ("ty", "Paper type", lambda p: p.get("type"), ["Method", "Benchmark", "Analysis", "User study", "Survey / position"]),
        ("ml", "Model", lambda p: p.get("model"), ["LLM", "VLM", "Embodied / VLA", "Speech", "None"]),
    ]
    shift_attrs = []
    for k, name, get, order in attr_defs:
        rows = []
        for v in order:
            a_ = round(100 * sum(get(p) == v for p in early_ps) / max(1, len(early_ps)))
            b_ = round(100 * sum(get(p) == v for p in recent_ps) / max(1, len(recent_ps)))
            if a_ or b_:
                rows.append({"v": v, "a": a_, "b": b_, "d": b_ - a_})
        top = max([max(r["a"], r["b"]) for r in rows] + [10])
        mx = min(100, -(-top // 10) * 10)
        for r in rows:
            r["pa"], r["pb"] = round(100 * r["a"] / mx, 1), round(100 * r["b"] / mx, 1)
        shift_attrs.append({"k": k, "name": name, "rows": rows, "max": mx})
    shift = {"attrs": shift_attrs, "early_label": f"up to {this_year - 2}", "recent_label": f"{this_year - 1}–{str(this_year)[2:]}",
             "n_early": len(early_ps), "n_recent": len(recent_ps)}

    env = Environment(loader=FileSystemLoader(ROOT / "templates"), autoescape=select_autoescape(["html"]))
    common = {"site": site, "repo": repo, "branch": branch, "sections": sections, "sec_by_key": sec_by_key,
              "n_featured": len(picks),
              "giscus": giscus, "built": dt.date.today().isoformat(),
              "v": dt.datetime.now().strftime("%Y%m%d%H%M%S")}

    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "p").mkdir(parents=True)
    shutil.copytree(ROOT / "static", OUT / "static")
    (OUT / ".nojekyll").write_text("")
    if (ROOT / "thumbs").exists():
        shutil.copytree(ROOT / "thumbs", OUT / "thumbs")

    index_data = [{
        "slug": p["slug"], "t": p["title"], "y": p.get("year") or "", "v": p.get("venue") or "",
        "s": p.get("section") or "", "ty": p.get("type") or "", "tp": p.get("topic") or "",
        "m": p.get("summary") or "", "a": [n["author"] for n in p["notes"]], "last": p["last"],
        "al": p.get("also") or [], "u": p.get("user") or "", "tr": p.get("training") or "",
        "mo": p.get("modality") or [], "ml": p.get("model") or "",
        "th": p["thumb"], "f": 1 if p["featured"] else 0, "fr": p["featured"]["rank"] if p["featured"] else 999,
        "st": p.get("status") or "preprint", "va": p["venue_group"], "k": p["kind"], "ax": p["arxiv_label"],
    } for p in plist]
    data_json = json.dumps(index_data, ensure_ascii=False).replace("</", "<\\/")
    (OUT / "index.html").write_text(
        env.get_template("index.html").render(
            root="", page="papers", stats=stats, recent=recent, data_json=data_json, picks=picks,
            sec_meta=[{"k": s["key"], "c": s["color"], "code": s["code"], "d": s.get("desc", ""), "o": s["owners"],
                       "n": s["n"], "done": s["done"]} for s in sections], **common),
        encoding="utf8")

    for name, page in (("featured.html", "featured"),):   # overview.html is retired (kept in templates/)
        (OUT / name).write_text(env.get_template(name).render(root="", page=page, stats=stats, picks=picks, shift=shift, **common),
                                encoding="utf8")

    tpl = env.get_template("paper.html")
    for p in plist:
        d = OUT / "p" / p["slug"]
        d.mkdir()
        has_math = any('class="math' in n["html"] for n in p["notes"])
        (d / "index.html").write_text(
            tpl.render(root="../../", page="paper", paper=p, sec=sec_by_key.get(p.get("section")), has_math=has_math, **common),
            encoding="utf8")

    for w in warnings:
        print("Warning: " + w)
    print(f"Built {stats['papers']} papers, {stats['notes']} notes -> {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
