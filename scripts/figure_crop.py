"""Find a paper's first figure in its PDF and crop it.

Looks for the caption "Figure 1" (or "Fig. 1") on the first 8 pages, then takes the graphics
(embedded images and vector drawings) sitting directly above it in the same column. Returns
None when no caption or no graphics are found, so the caller can fall back to page 1.
"""
import re

import pymupdf as fitz

CAPTION = re.compile(r"^\s*(?:Figure|Fig\.?)\s*1\s*[:.|]", re.I)
MAX_PAGES = 8
GAP = 28          # pt: graphics further apart than this vertically are not the same figure
PAD = 4           # pt around the crop


def _caption(page):
    for b in page.get_text("blocks"):
        x0, y0, x1, y1, text = b[:5]
        if CAPTION.match(text):
            return fitz.Rect(x0, y0, x1, y1)
    return None


def _graphics(page):
    pr = page.rect
    rects = []
    for info in page.get_image_info():
        r = fitz.Rect(info["bbox"]) & pr
        if r.width > 8 and r.height > 8:
            rects.append(r)
    for d in page.get_drawings():
        r = fitz.Rect(d["rect"]) & pr
        if r.is_empty:
            continue
        if r.width > pr.width * 0.9 and r.height < 3:   # page-wide rules (headers, table lines)
            continue
        if r.width < 1 and r.height < 1:
            continue
        rects.append(r)
    return rects


def find_figure(doc):
    """Return (page_number, clip Rect) for Figure 1, or None."""
    for pno in range(min(MAX_PAGES, len(doc))):
        page = doc[pno]
        cap = _caption(page)
        if not cap:
            continue
        pr = page.rect
        mid = pr.width / 2
        # column of the caption: full width if it crosses the middle, else its half
        if cap.x0 < mid - 20 and cap.x1 > mid + 20:
            col = (pr.x0, pr.x1)
        elif cap.x1 <= mid + 20:
            col = (pr.x0, mid + 10)
        else:
            col = (mid - 10, pr.x1)
        cands = [r for r in _graphics(page)
                 if r.y1 <= cap.y0 + 6 and r.x0 >= col[0] - 2 and r.x1 <= col[1] + 2]
        if not cands:
            continue
        # grow a cluster upward from the graphics nearest the caption
        cands.sort(key=lambda r: -r.y1)
        top_edge = cands[0].y1
        if cap.y0 - top_edge > 60:          # nothing graphical right above the caption
            continue
        box = fitz.Rect(cands[0])
        for r in cands[1:]:
            if r.y1 >= box.y0 - GAP:
                box |= r
        # text labels inside the figure area are kept by the crop itself
        box = fitz.Rect(max(box.x0 - PAD, pr.x0), max(box.y0 - PAD, pr.y0),
                        min(box.x1 + PAD, pr.x1), min(max(box.y1, cap.y0 - 2) + PAD - 4, pr.y1))
        if box.height < 40 or box.width < 80:
            continue
        return pno, box
    return None


def render_clip(doc, pno, clip, width):
    page = doc[pno]
    zoom = width / clip.width
    return page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=clip, alpha=False)
