"""Make the pictures shown in the list and on the paper page.

For each paper: Figure 1 cropped from the PDF (figs/<paper id>.webp; see figure_crop.py), and a
small image of page 1 (thumbs/<paper id>.webp), used when the paper has no Figure 1. Papers whose
PDF has no Figure 1 are listed in figs/none.txt so they are not downloaded again. To replace a
crop by hand, overwrite figs/<paper id>.webp; it is never regenerated once it exists.

Only papers that someone has written a note for get one, so downloads follow what the group
actually reads. The deploy workflow runs this on every push, so a new note gets its thumbnail
automatically.

    python scripts/make_thumbs.py            # noted papers that have no thumbnail yet
    python scripts/make_thumbs.py --all      # every arXiv paper (about 700 downloads; not needed normally)

Downloads each arXiv paper's PDF (one request every 3 seconds, as arXiv asks for automated
access), saves the two images (~10-60 KB each) and throws the PDF away. Papers that are not on arXiv are skipped. Re-running only fetches what is missing.
Needs: pip install pymupdf pillow
"""
import argparse
import io
import pathlib
import re
import sys
import time
import urllib.request

import pymupdf as fitz
import yaml
from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from figure_crop import find_figure, render_clip  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "thumbs"
FIGS = ROOT / "figs"
NONE = FIGS / "none.txt"
UA = "IIA-paper-reading-thumbnails/1.0 (https://github.com/IIA-research/paper-reading)"
DELAY = 3.0


def slugify(pid):
    return re.sub(r"[^A-Za-z0-9._-]+", "-", str(pid)).strip("-") or "paper"


def arxiv_id(p):
    m = re.search(r"arxiv\.org/(?:abs|pdf)/([0-9]{4}\.[0-9]{4,5})", p.get("url") or "")
    return m.group(1) if m else None


def webp(pix, quality):
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    buf = io.BytesIO()
    img.save(buf, "WEBP", quality=quality, method=6)
    return buf.getvalue()


def render(doc, width=300):
    page = doc[0]
    zoom = width / page.rect.width
    return webp(page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False), 72)


def figure(doc, width=640):
    found = find_figure(doc)
    return webp(render_clip(doc, *found, width), 80) if found else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="every arXiv paper, not only noted ones")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    FIGS.mkdir(exist_ok=True)
    nofig = set(NONE.read_text().split()) if NONE.exists() else set()
    papers = yaml.safe_load((ROOT / "papers.yaml").read_text(encoding="utf8"))
    noted = {d.name for d in (ROOT / "notes").glob("*") if d.is_dir() and any(d.glob("*.md"))}
    pool = papers if args.all else [p for p in papers if slugify(p["id"]) in noted]
    for p in pool:
        if not arxiv_id(p):
            print(f"  skip {p['id']}: not on arXiv")
    def missing(p):
        slug = slugify(p["id"])
        return not (OUT / f"{slug}.webp").exists() or (
            not (FIGS / f"{slug}.webp").exists() and slug not in nofig)
    todo = [p for p in pool if arxiv_id(p) and missing(p)]
    if args.limit:
        todo = todo[: args.limit]
    print(f"pictures: {len(todo)} papers to fetch")
    if not todo:
        return
    done = failed = 0
    for i, p in enumerate(todo, 1):
        aid = arxiv_id(p)
        try:
            req = urllib.request.Request(f"https://arxiv.org/pdf/{aid}", headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                pdf = r.read()
            slug = slugify(p["id"])
            doc = fitz.open(stream=pdf, filetype="pdf")
            if not (OUT / f"{slug}.webp").exists():
                (OUT / f"{slug}.webp").write_bytes(render(doc))
            if not (FIGS / f"{slug}.webp").exists():
                fig = figure(doc)
                if fig:
                    (FIGS / f"{slug}.webp").write_bytes(fig)
                else:
                    nofig.add(slug)
                    print(f"  {aid}: no Figure 1 found, page 1 is used")
            done += 1
        except Exception as e:  # keep going; a re-run retries the failures
            failed += 1
            print(f"  {aid}: {e}", file=sys.stderr)
        if i % 25 == 0:
            print(f"  {i}/{len(todo)}")
        time.sleep(DELAY)
    NONE.write_text("".join(f"{s}\n" for s in sorted(nofig)))
    print(f"done: {done} new, {failed} failed")


if __name__ == "__main__":
    main()
