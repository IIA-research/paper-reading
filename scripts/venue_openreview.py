"""Exact-title lookup on OpenReview for papers with no acceptance evidence yet. Caches to openreview.json."""
import json, re, sys, time, pathlib, urllib.request, urllib.parse, yaml
d = pathlib.Path(sys.argv[1])
D = json.load(open(d / "decided.json"))
P = {str(p["id"]): p for p in yaml.safe_load(open("papers.yaml", encoding="utf8"))}
cache_f = d / "openreview.json"
cache = json.load(open(cache_f)) if cache_f.exists() else {}
norm = lambda t: re.sub(r"[^a-z0-9]", "", (t or "").lower())
todo = [pid for pid, x in D.items() if x["status"] == "preprint" and pid not in cache]
print("to look up:", len(todo))
for i, pid in enumerate(todo):
    title = P[pid]["title"]
    url = "https://api2.openreview.net/notes/search?" + urllib.parse.urlencode({"term": title, "type": "terms", "source": "forum", "limit": 10})
    hits = []
    for attempt in range(4):
        try:
            data = json.load(urllib.request.urlopen(url, timeout=60)); break
        except Exception as e:
            time.sleep(5 * (attempt + 1)); data = {"notes": []}
    for n in data.get("notes", []):
        c = n.get("content", {})
        t = (c.get("title") or {}).get("value") if isinstance(c.get("title"), dict) else c.get("title")
        if norm(t) != norm(title): continue
        v = c.get("venue"); vid = c.get("venueid")
        hits.append({"venue": v.get("value") if isinstance(v, dict) else v, "venueid": vid.get("value") if isinstance(vid, dict) else vid})
    cache[pid] = hits
    if i % 25 == 0:
        cache_f.write_text(json.dumps(cache, indent=1)); print(i, end=" ", flush=True)
    time.sleep(1.0)
cache_f.write_text(json.dumps(cache, indent=1))
print("\ndone", sum(1 for v in cache.values() if v), "with exact-title hits")
