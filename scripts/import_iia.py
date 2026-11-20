"""One-off import: read the paper data out of the IIA literature-map page and write papers.yaml.

Usage:
    python scripts/import_iia.py <IIA map index.html> [--translations FILE.json] [--include-out]

The IIA map stores topics and summaries in Chinese. Pass --translations with a JSON object
{paper id: {"topic": ..., "summary": ...}} to use English versions instead.
Papers in the "out of scope" chapter are skipped unless --include-out is given.
"""
import argparse
import json
import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent

SECTION = {"理解": "Understanding", "求证": "Elicitation", "执行": "Execution", "交代": "Reporting",
           "跟踪": "Tracking", "评测": "Evaluation", "训练": "Training", "范围外": "Out of scope"}
TYPE = {"方法": "Method", "benchmark": "Benchmark", "分析": "Analysis", "用户研究": "User study",
        "综述/立场": "Survey / position"}
VENUE = {"未知": "Unknown"}
USER = {"真人": "Human", "用户模拟器": "User simulator", "静态数据集": "Static dataset", "无": "None", "未说明": "Unspecified"}
TRAINING = {"免训练": "Training-free", "偏好优化": "Preference optimization", "N/A": "Not applicable"}
MODALITY = {"文本": "Text", "图像": "Image", "视频": "Video", "音频": "Audio", "具身": "Embodied", "不涉及": "None"}
MODEL = {"具身/VLA": "Embodied / VLA", "语音": "Speech", "不涉及": "None"}


def load_all(html_path):
    for line in pathlib.Path(html_path).read_text(encoding="utf8").split("\n"):
        if line.startswith("const ALL = "):
            return json.loads(line[line.index("["): line.rindex("]") + 1])
    sys.exit("Could not find `const ALL = [...]`; is this the IIA map page?")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("html")
    ap.add_argument("--translations")
    ap.add_argument("--include-out", action="store_true")
    args = ap.parse_args()
    tr = json.loads(pathlib.Path(args.translations).read_text(encoding="utf8")) if args.translations else {}

    papers, missing = [], 0
    for d in load_all(args.html):
        if d["c"] == "范围外" and not args.include_out:
            continue
        t = tr.get(str(d["id"]))
        if args.translations and not t:
            missing += 1
        papers.append({
            "id": d["id"],
            "title": d["t"],
            "url": d["u"],
            "year": d["y"],
            "venue": VENUE.get(d["v"], d["v"]),
            "section": SECTION.get(d["c"], d["c"]),
            "also": [SECTION.get(a, a) for a in d.get("a") or []],
            "type": TYPE.get(d["ty"], d["ty"]),
            "user": USER.get(d.get("e"), d.get("e") or ""),
            "training": TRAINING.get(d.get("tr"), d.get("tr") or ""),
            "modality": [MODALITY.get(m, m) for m in d.get("mo") or []],
            "model": MODEL.get(d.get("ml"), d.get("ml") or ""),
            "topic": (t or {}).get("topic", d.get("s") or ""),
            "summary": (t or {}).get("summary", d.get("m") or ""),
        })
    papers.sort(key=lambda p: (-int(p["year"] or 0), p["title"].lower()))
    head = ("# Paper list, one entry per paper. Do not change `id`: note folders and comment threads are keyed on it.\n"
            "# `section` must be one of the section keys in site.yaml.\n\n")
    out = ROOT / "papers.yaml"
    out.write_text(head + yaml.safe_dump(papers, allow_unicode=True, sort_keys=False, width=1000), encoding="utf8")
    print(f"Wrote {len(papers)} papers to {out.relative_to(ROOT)}" + (f" ({missing} without a translation)" if missing else ""))


if __name__ == "__main__":
    main()
