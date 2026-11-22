"""Fetch venue evidence for every paper: Semantic Scholar batch + arXiv comment/journal_ref."""
import json, re, sys, time, pathlib, urllib.request, urllib.parse
import xml.etree.ElementTree as ET
import yaml
OUT = pathlib.Path(sys.argv[1])
papers = yaml.safe_load(open("papers.yaml", encoding="utf8"))
def s2id(p):
    u = p.get("url") or ""
    m = re.search(r"arxiv\.org/(?:abs|pdf)/([0-9]{4}\.[0-9]{4,5})", u)
    if m: return "ARXIV:" + m.group(1)
    m = re.search(r"doi\.org/(10\..+)$", u)
    if m: return "DOI:" + m.group(1)
    m = re.search(r"semanticscholar\.org/paper/([0-9a-f]{40})", u)
    if m: return m.group(1)
    m = re.search(r"aclanthology\.org/([^/]+?)(?:\.pdf)?/?$", u)
    if m: return "ACL:" + m.group(1)
    return None
ids = {str(p["id"]): s2id(p) for p in papers}
(OUT / "ids.json").write_text(json.dumps(ids, indent=1))
fields = "title,venue,year,journal,publicationVenue,externalIds,publicationTypes,publicationDate"
q = [v for v in ids.values() if v]
res = {}
for i in range(0, len(q), 400):
    chunk = q[i:i+400]
    req = urllib.request.Request(f"https://api.semanticscholar.org/graph/v1/paper/batch?fields={fields}",
                                 data=json.dumps({"ids": chunk}).encode(), headers={"Content-Type": "application/json"})
    for attempt in range(5):
        try:
            data = json.load(urllib.request.urlopen(req, timeout=120)); break
        except Exception as e:
            print("s2 retry", attempt, e); time.sleep(10 * (attempt + 1))
    for k, d in zip(chunk, data): res[k] = d
    time.sleep(3)
(OUT / "s2.json").write_text(json.dumps(res, indent=1))
print("s2 got", sum(1 for v in res.values() if v), "of", len(q))
# arXiv comments + journal_ref
ax = [v[6:] for v in q if v.startswith("ARXIV:")]
ns = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}
arx = {}
for i in range(0, len(ax), 100):
    chunk = ax[i:i+100]
    url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode({"id_list": ",".join(chunk), "max_results": len(chunk)})
    for attempt in range(5):
        try:
            root = ET.fromstring(urllib.request.urlopen(url, timeout=120).read()); break
        except Exception as e:
            print("arxiv retry", attempt, e); time.sleep(10 * (attempt + 1))
    for e in root.findall("a:entry", ns):
        aid = re.sub(r"v\d+$", "", e.findtext("a:id", "", ns).rsplit("/abs/", 1)[-1])
        arx[aid] = {"comment": (e.findtext("x:comment", "", ns) or "").strip(), "journal_ref": (e.findtext("x:journal_ref", "", ns) or "").strip()}
    time.sleep(3.5)
(OUT / "arxiv.json").write_text(json.dumps(arx, indent=1, ensure_ascii=False))
print("arxiv got", len(arx), "of", len(ax))
