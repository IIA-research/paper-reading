"""Build the site: read site.yaml, papers.yaml and notes/, write to _site/.

    python build.py                          # build
    python -m http.server -d _site 8000      # preview at http://localhost:8000
"""
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
    stats = {
        "papers": len(plist),
        "with_notes": sum(1 for p in plist if p["notes"]),
        "notes": len(all_notes),
        "people": len({n["author"] for n, _ in all_notes} | {o for s in sections for o in s["owners"]}),
    }

    gc = site.get("giscus") or {}
    giscus = None
    if gc.get("repo_id") and gc.get("category_id"):
        giscus = {"repo": repo, **gc}

    env = Environment(loader=FileSystemLoader(ROOT / "templates"), autoescape=select_autoescape(["html"]))
    common = {"site": site, "repo": repo, "branch": branch, "sections": sections, "sec_by_key": sec_by_key,
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
    } for p in plist]
    data_json = json.dumps(index_data, ensure_ascii=False).replace("</", "<\\/")
    (OUT / "index.html").write_text(
        env.get_template("index.html").render(
            root="", stats=stats, recent=recent, data_json=data_json, picks=picks,
            sec_meta=[{"k": s["key"], "c": s["color"], "code": s["code"], "d": s.get("desc", ""), "o": s["owners"],
                       "n": s["n"], "done": s["done"]} for s in sections], **common),
        encoding="utf8")

    tpl = env.get_template("paper.html")
    for p in plist:
        d = OUT / "p" / p["slug"]
        d.mkdir()
        has_math = any('class="math' in n["html"] for n in p["notes"])
        (d / "index.html").write_text(
            tpl.render(root="../../", paper=p, sec=sec_by_key.get(p.get("section")), has_math=has_math, **common),
            encoding="utf8")

    for w in warnings:
        print("Warning: " + w)
    print(f"Built {stats['papers']} papers, {stats['notes']} notes -> {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
