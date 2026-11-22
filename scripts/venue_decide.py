"""Decide each paper's publication status from the fetched evidence.

status: published (indexed proceedings / journal / ACL Anthology / publisher DOI)
        accepted  (authors' arXiv comment or journal_ref says accepted/appearing, not yet indexed)
        workshop  (any evidence says workshop)
        preprint  (no evidence of acceptance)
"""
import json, re, sys, yaml, collections
d = sys.argv[1]
ids = json.load(open(d + "/ids.json")); s2 = json.load(open(d + "/s2.json")); ax = json.load(open(d + "/arxiv.json"))
papers = yaml.safe_load(open("papers.yaml", encoding="utf8"))
import os
OR = json.load(open(d + "/openreview.json")) if os.path.exists(d + "/openreview.json") else {}
S2NAMES = [("Findings of the Association", "ACL"), ("Empirical Methods in Natural Language Processing", "EMNLP"), ("Annual Meeting of the Association for Computational Linguistics", "ACL"),
           ("North American Chapter", "NAACL"), ("European Chapter", "EACL"), ("International Conference on Learning Representations", "ICLR"),
           ("Neural Information Processing Systems", "NeurIPS"), ("International Conference on Machine Learning", "ICML"), ("AAAI Conference", "AAAI"),
           ("International Conference on Computational Linguistics", "COLING"), ("Human Factors in Computing Systems", "CHI"), ("Intelligent User Interfaces", "IUI"),
           ("Knowledge Discovery and Data Mining", "KDD"), ("Research and Development in Information Retrieval", "SIGIR"), ("The Web Conference", "WWW"),
           ("World Wide Web", "WWW"), ("Trans. Mach. Learn. Res", "TMLR"), ("Transactions of the Association for Computational Linguistics", "TACL"),
           ("Conference on Language Modeling", "COLM"), ("Conference on Robot Learning", "CoRL"), ("Information and Knowledge Management", "CIKM"),
           ("Web Search and Data Mining", "WSDM"), ("International Joint Conference on Artificial Intelligence", "IJCAI"), ("Computer Vision and Pattern Recognition", "CVPR"),
           ("Robotics and Automation", "ICRA"), ("Intelligent Robots and Systems", "IROS"), ("Human-Robot Interaction", "HRI"), ("Recommender Systems", "RecSys"),
           ("Autonomous Agents and Multiagent", "AAMAS"), ("Internet and Network Economics", "WINE"), ("SIGDIAL", "SIGDIAL"), ("Language Resources and Evaluation", "LREC"),
           ("Computer-Supported Cooperative Work", "CSCW"), ("User Interface Software and Technology", "UIST")]

DBLP = {"acl": "ACL", "emnlp": "EMNLP", "naacl": "NAACL", "eacl": "EACL", "coling": "COLING", "lrec": "LREC", "iclr": "ICLR", "nips": "NeurIPS",
        "icml": "ICML", "chi": "CHI", "www": "WWW", "iui": "IUI", "sigir": "SIGIR", "fat": "FAccT", "aaai": "AAAI", "uist": "UIST", "cikm": "CIKM",
        "ci": "Collective Intelligence", "re": "RE", "ro-man": "RO-MAN", "chiir": "CHIIR", "aied": "AIED", "kdd": "KDD", "kbse": "ASE", "natmi": "Nature Machine Intelligence", "chb": "Computers in Human Behavior", "sigdial": "SIGDIAL",
        "sigsoft": "FSE", "ijcnn": "IJCNN", "ACMdis": "DIS", "pacmhci": "PACM HCI", "tacl": "TACL", "tois": "ACM TOIS", "ijcai": "IJCAI",
        "corl": "CoRL", "icra": "ICRA", "iros": "IROS", "hri": "HRI", "cscw": "CSCW", "recsys": "RecSys", "wsdm": "WSDM", "cvpr": "CVPR",
        "iccv": "ICCV", "eccv": "ECCV", "aamas": "AAMAS", "uai": "UAI", "aistats": "AISTATS", "interspeech": "Interspeech", "icassp": "ICASSP",
        "tmlr": "TMLR", "jair": "JAIR", "colm": "COLM", "sigdial": "SIGDIAL", "mm": "ACM MM", "nlpcc": "NLPCC", "ecir": "ECIR", "ictir": "ICTIR"}
ACRO = r"(?i:(?<![A-Za-z])(ACL|EMNLP|NAACL|EACL|AACL|COLING|LREC|ICLR|ICML|NeurIPS|NIPS|AAAI|IJCAI|CHI|CSCW|UIST|IUI|KDD|SIGIR|WWW|TheWebConf|Web Conference|CIKM|WSDM|RecSys|COLM|CoRL|ICRA|IROS|RSS|HRI|CVPR|ICCV|ECCV|TACL|TMLR|JAIR|AAMAS|SIGDIAL|INTERSPEECH|Interspeech|ICASSP|UAI|AISTATS|ACM MM|ECIR|ICTIR|CHIIR|FAccT|TOIS|TASLP|IEEE TASLP|PRIMA|WINE|ICCE|EurIPS|AIES|ICWSM|EMNLP-IJCNLP|Nature|Science|PNAS)(?![A-Za-z]))"
NEG = re.compile(r"under review|submitted|in submission|preprint|work in progress|draft", re.I)
POS = re.compile(r"accept|to appear|appear(s|ing)? (at|in)|published|camera[- ]ready|proceedings|main conference|oral|spotlight|poster", re.I)

def acl_venue(aid):  # ACL Anthology id like 2025.naacl-long.170 / 2023.findings-emnlp.12 / 2026.lrec-1.547
    m = re.match(r"(\d{4})\.([a-z]+)(?:-([a-z]+))?", aid or "")
    if not m: return None
    yr, a, b = m.groups()
    if a == "findings": return f"{(b or '').upper()} {yr} Findings", "published"
    name = {"tacl": "TACL", "cl": "Computational Linguistics"}.get(a, a.upper())
    if b and b not in ("long", "short", "main", "demo", "demos", "industry", "srw", "tutorials", "1", "2"):
        return f"{name} {yr} Workshop ({b})", "workshop"
    return f"{name} {yr}", "published"

def from_text(t):
    """Venue named in an arXiv comment / journal_ref, if it reads as an acceptance."""
    if not t or (NEG.search(t) and not POS.search(t)): return None
    m = re.search(ACRO + r"[\s'’(-]*((?:19|20)\d{2}|'\d{2})?", t)
    if not m: return None
    raw = m.group(1)
    canon = {"nips": "NeurIPS", "neurips": "NeurIPS", "thewebconf": "WWW", "web conference": "WWW", "interspeech": "Interspeech", "ieee taslp": "TASLP", "eurips": "EurIPS", "colm": "COLM", "emnlp-ijcnlp": "EMNLP"}
    ac = canon.get(raw.lower(), raw.upper() if raw.isalpha() and len(raw) <= 6 and raw.lower() not in ("nature", "science") else raw)
    yr = m.group(2) or ""
    if yr and len(yr.strip("'")) == 2: yr = "20" + yr.strip("'")
    v = f"{ac} {yr}".strip()
    if re.search(r"findings", t, re.I): v += " Findings"
    if re.search(r"workshop", t, re.I): return v + " Workshop", "workshop"
    return v, "accepted"

out, rows = {}, []
for p in papers:
    pid, url = str(p["id"]), p.get("url") or ""
    k = ids.get(pid); r = s2.get(k) if k else None
    e = (r or {}).get("externalIds") or {}
    ev, venue, status = [], None, "preprint"
    # 1. authoritative: ACL Anthology, DBLP proceedings/journal, publisher DOI
    m = re.search(r"aclanthology\.org/([^/]+?)(?:\.pdf)?/?$", url)
    a = acl_venue(m.group(1) if m else e.get("ACL"))
    if a: venue, status = a; ev.append("ACL Anthology")
    key = e.get("DBLP") or ""
    if not venue and key and not key.startswith("journals/corr"):
        parts = key.split("/")
        name = DBLP.get(parts[1], parts[1].upper())
        m2 = re.search(r"(\d{2})$", parts[-1])          # DBLP keys end in the proceedings year, e.g. ZhangKC25
        yr = ("20" + m2.group(1)) if m2 and int(m2.group(1)) < 50 else ("19" + m2.group(1)) if m2 else ((r or {}).get("year") or p.get("year"))
        venue, status = f"{name} {yr}", "published"; ev.append("DBLP " + key)
    doi = e.get("DOI") or ""
    if not venue and doi and not doi.startswith("10.48550"):
        jn = ((r or {}).get("journal") or {}).get("name") or (r or {}).get("venue") or ""
        pv = ((r or {}).get("publicationVenue") or {})
        short = next((x for x in pv.get("alternate_names", []) if x.isupper() and len(x) <= 8), None)
        venue, status = f"{short or jn or p['venue']} {(r or {}).get('year') or p.get('year')}".strip(), "published"; ev.append("DOI " + doi)
    # 2. OpenReview: only formally accepted papers (conference track, TMLR, workshop); submissions, ARR, rejected, withdrawn are ignored
    or_pick = None
    if not venue:
        for h in OR.get(pid, []):
            vn, vid = h.get("venue") or "", h.get("venueid") or ""
            if re.search(r"Submission|Under_Review|Rejected|Withdrawn|Desk|journals/CORR", vid) or re.match(r"(Submitted|CoRR|arXiv|Under review)", vn): continue
            m_ = re.match(r"([A-Za-z.]+?)(?:\.cc|\.org)?/(?:COLM/)?(\d{4})/(Conference|Workshop)(?:/([^/]+))?$", vid)
            if m_:
                conf = {"ICLR": "ICLR", "NeurIPS": "NeurIPS", "ICML": "ICML", "colmweb": "COLM", "AAAI": "AAAI"}.get(m_.group(1).split(".")[0], m_.group(1).split(".")[0])
                if m_.group(3) == "Workshop":
                    cand = (f"{conf} {m_.group(2)} Workshop ({m_.group(4)})", "workshop")
                else:
                    cand = (f"{conf} {m_.group(2)}", "accepted")
            elif vid == "TMLR":
                cand = ("TMLR", "accepted")
            elif vid.startswith("dblp.org/conf/") or vid.startswith("dblp.org/journals/"):
                cand = (re.sub(r"\s*\(\d\)", "", vn), "published")
            elif vid.startswith("OpenReview.net/"):   # publication record added by the authors, e.g. "ACL (1) 2026", "Science"
                cand = (re.sub(r"\s*\(\d\)", "", vn), "accepted")
            else:
                cand = (vn, "workshop" if re.search(r"workshop|meeting", vid, re.I) else "accepted")
            if or_pick is None or (or_pick[1] == "workshop" and cand[1] != "workshop"): or_pick = cand
        if or_pick and or_pick[1] != "workshop":
            venue, status = or_pick; ev.append("OpenReview: " + venue)
    # 3. Semantic Scholar's venue field (links the arXiv record to the published version)
    sv = (r or {}).get("venue") or ""
    if not venue and sv and "arxiv" not in sv.lower():
        ac = next((a_ for k_, a_ in S2NAMES if k_ in sv), None)
        yr = (re.search(r"(?:19|20)\d{2}", sv) or [None])[0]
        iia = p.get("venue") or ""
        if not yr and ac and iia.upper().startswith(ac.upper()):
            venue = iia
        else:
            venue = f"{ac or sv[:60]} {yr or (r or {}).get('year') or ''}".strip()
            if "findings" in (sv + iia).lower() and "Findings" not in venue: venue += " Findings"
        status = "workshop" if "workshop" in sv.lower() else "accepted"; ev.append("Semantic Scholar venue: " + sv[:80])
    if not venue and or_pick:
        venue, status = or_pick; ev.append("OpenReview: " + venue)
    # 4. authors' own statement on arXiv
    aid = (k or "")[6:] if (k or "").startswith("ARXIV:") else re.search(r"arxiv\.org/abs/([\d.]+)", url).group(1) if "arxiv.org/abs/" in url else None
    axr = ax.get(aid or "", {})
    txt = " | ".join(x for x in (axr.get("journal_ref"), axr.get("comment")) if x)
    t = from_text(txt) if txt else None
    if t and t[1]:
        if not venue:
            venue, status = t; ev.append("arXiv comment: " + txt[:120])
        elif t[1] == "workshop" and status == "published" and "Workshop" not in venue:
            ev.append("arXiv comment mentions workshop: " + txt[:80])
    # 3. known classics without machine-readable records
    if not venue and not k and p.get("venue") not in ("arXiv", "Unknown", None):
        venue = p["venue"]; status = "workshop" if "workshop" in venue.lower() else "published"; ev.append("official page (" + url + ")")
    if not venue and p.get("venue") not in ("arXiv", "Unknown", None):
        venue, status = p["venue"], "unverified"; ev.append("IIA map says " + p["venue"] + "; no source confirms it")
    if not venue: venue = "arXiv"
    out[pid] = {"venue": venue, "status": status, "evidence": "; ".join(ev) or "no acceptance found (Semantic Scholar, DBLP via S2, arXiv comment)"}
    rows.append((pid, p.get("venue"), venue, status))
json.dump(out, open(d + "/decided2.json", "w"), indent=1, ensure_ascii=False)
print(collections.Counter(s for *_, s in rows))
def norm(v): return re.sub(r"[^a-z0-9]", "", (v or "").lower())
chg = [(pid, old, new, st) for pid, old, new, st in rows if norm(old) != norm(new)]
print("venue text changed:", len(chg))
flips = collections.Counter((("arXiv" if old in ("arXiv", "Unknown") else "venue"), ("arXiv" if st == "preprint" else st)) for pid, old, new, st in rows)
print(flips)
json.dump(chg, open(d + "/changes2.json", "w"), indent=1, ensure_ascii=False)
