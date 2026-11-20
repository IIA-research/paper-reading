"""Make a small image of a paper's first page, shown in the list and on the paper page.

Only papers that someone has written a note for get one, so downloads follow what the group
actually reads. The deploy workflow runs this on every push, so a new note gets its thumbnail
automatically.

    python scripts/make_thumbs.py            # noted papers that have no thumbnail yet
    python scripts/make_thumbs.py --all      # every arXiv paper (about 700 downloads; not needed normally)

Downloads each arXiv paper's PDF (one request every 3 seconds, as arXiv asks for automated
access), renders page 1 at 300 px wide, saves thumbs/<paper id>.webp (~10-25 KB) and throws the
PDF away. Papers that are not on arXiv are skipped. Re-running only fetches what is missing.
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

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "thumbs"
UA = "IIA-paper-reading-thumbnails/1.0 (https://github.com/IIA-research/paper-reading)"
DELAY = 3.0


def slugify(pid):
    return re.sub(r"[^A-Za-z0-9._-]+", "-", str(pid)).strip("-") or "paper"


def arxiv_id(p):
    m = re.search(r"arxiv\.org/(?:abs|pdf)/([0-9]{4}\.[0-9]{4,5})", p.get("url") or "")
    return m.group(1) if m else None


def render(pdf_bytes, width=300):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc[0]
    zoom = width / page.rect.width
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    buf = io.BytesIO()
    img.save(buf, "WEBP", quality=72, method=6)
    return buf.getvalue()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="every arXiv paper, not only noted ones")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    papers = yaml.safe_load((ROOT / "papers.yaml").read_text(encoding="utf8"))
    noted = {d.name for d in (ROOT / "notes").glob("*") if d.is_dir() and any(d.glob("*.md"))}
    pool = papers if args.all else [p for p in papers if slugify(p["id"]) in noted]
    for p in pool:
        if not arxiv_id(p):
            print(f"  skip {p['id']}: not on arXiv")
    todo = [p for p in pool if arxiv_id(p) and not (OUT / f"{slugify(p['id'])}.webp").exists()]
    if args.limit:
        todo = todo[: args.limit]
    print(f"thumbnails: {len(todo)} to fetch")
    if not todo:
        return
    done = failed = 0
    for i, p in enumerate(todo, 1):
        aid = arxiv_id(p)
        try:
            req = urllib.request.Request(f"https://arxiv.org/pdf/{aid}", headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                pdf = r.read()
            (OUT / f"{slugify(p['id'])}.webp").write_bytes(render(pdf))
            done += 1
        except Exception as e:  # keep going; a re-run retries the failures
            failed += 1
            print(f"  {aid}: {e}", file=sys.stderr)
        if i % 25 == 0:
            print(f"  {i}/{len(todo)}")
        time.sleep(DELAY)
    print(f"done: {done} new, {failed} failed")


if __name__ == "__main__":
    main()
