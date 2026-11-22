"""Clean venue labels, keep IIA's more specific label when it agrees with the evidence, and flag conflicts."""
import json, re, sys, yaml, collections, importlib.util
d = sys.argv[1]
spec = importlib.util.spec_from_file_location("dec", d + "/decide2.py")
D = json.load(open(d + "/decided2.json"))
P = {str(p["id"]): p for p in yaml.safe_load(open("papers.yaml", encoding="utf8"))}
LONG = [("Findings of the Association", "ACL"), ("Empirical Methods in Natural Language Processing", "EMNLP"), ("Association for Computational Linguistics", "ACL"),
        ("North American Chapter", "NAACL"), ("European Chapter", "EACL"), ("Learning Representations", "ICLR"), ("Neural Information Processing", "NeurIPS"),
        ("International Conference on Machine Learning", "ICML"), ("AAAI Spring Symposi", "AAAI Spring Symposium"), ("AAAI Conference", "AAAI"),
        ("Computational Linguistics", "COLING"), ("Human Factors in Computing", "CHI"), ("Intelligent User Interfaces", "IUI"), ("Knowledge Discovery", "KDD"),
        ("European Conference on Information Retrieval", "ECIR"), ("Retrieval", "SIGIR"), ("Fairness, Accountability", "FAccT"), ("Multi-Agent", "AAMAS"), ("Uncertainty in Artificial Intelligence", "UAI"), ("Web Conference", "WWW"), ("World Wide Web", "WWW"), ("Trans. Mach. Learn", "TMLR"), ("Language Modeling", "COLM"),
        ("Robot Learning", "CoRL"), ("Information and Knowledge Management", "CIKM"), ("Web Search and Data Mining", "WSDM"), ("Joint Conference on Artificial Intelligence", "IJCAI"),
        ("Computer Vision and Pattern", "CVPR"), ("Robotics and Automation", "ICRA"), ("Intelligent Robots", "IROS"), ("Human-Robot Interaction", "HRI"),
        ("Recommender Systems", "RecSys"), ("Multiagent", "AAMAS"), ("Internet and Network Economics", "WINE"), ("Language Resources and Evaluation", "LREC"),
        ("Cooperative Work", "CSCW"), ("User Interface Software", "UIST"), ("International Conference on Multimedia", "ACM MM"), ("Software Engineering and Methodology", "TOSEM"),
        ("Programming Languages", "PACMPL"), ("Information Processing", "IP&M"), ("Visualization and Computer Graphics", "TVCG"), ("Audio, Speech", "TASLP"),
        ("European Conference on Information Retrieval", "ECIR"), ("Management of Data", "SIGMOD"), ("AI Mag", "AI Magazine"), ("Computers in Education", "ICCE"),
        ("Workshop on Artificial Intelligence and Security", "AISec"), ("Conference on AI and Agentic Systems", "CAIS")]
def acr_of(s):
    if not s: return None
    for k, a in LONG:
        if k.lower() in s.lower(): return a
    m = re.match(r"([A-Za-z][A-Za-z&@.\-]*)", s.strip())
    return m.group(1) if m else None
def acl_doi(ev):
    m = re.search(r"DOI 10\.18653/(?:v1/)?(\d{4})\.([a-z]+)-([a-z]+)", ev)
    if not m: return None
    yr, a, b = m.groups()
    if a == "findings": return f"{b.upper()} {yr} Findings"
    return f"{a.upper()} {yr}" + (" Demo" if b.startswith("demo") else "")
out, conflicts, unver = {}, [], []
for pid, x in D.items():
    iia, st, lab, ev = P[pid]["venue"], x["status"], x["venue"], x["evidence"]
    lab = re.sub(r"\s+(regular|Main Track|Main|Conference Track|Oral|Poster|Spotlight|Track)$", "", lab, flags=re.I)
    a = acl_doi(ev)
    if a: lab = a
    yr = (re.search(r"(?:19|20)\d{2}", lab) or [None])[0]
    acr = acr_of(lab)
    iia_real = iia not in ("arXiv", "Unknown", None)
    if st in ("preprint",):
        lab = "arXiv"
    elif st == "unverified":
        unver.append(pid)
    else:
        iia_acr = acr_of(iia) if iia_real else None
        SAME = [{"CSCW", "PACM"}, {"PLDI", "PACMPL"}, {"ASE", "KBSE"}, {"FSE", "ESEC/FSE"}]
        compatible = iia_real and iia_acr and acr and (iia_acr.lower() in lab.lower() or acr.lower() in iia.lower() or iia_acr.lower() == acr.lower()
                                                     or any(iia_acr in g and acr in g for g in SAME) or "DOI" in ev[:4] or "Proceedings" in lab)
        wrong_kind = st == "workshop" and iia_real and "workshop" not in iia.lower()
        if compatible and not wrong_kind and not a:
            iy = (re.search(r"(?:19|20)\d{2}", iia) or [None])[0]
            lab = iia if (not yr or not iy or iy == yr or "DBLP" not in ev) else iia.replace(iy, yr)
        else:
            if acr and len(lab) > 30: lab = f"{acr} {yr or P[pid].get('year')}" + (" Workshop" if st == "workshop" else "")
            if iia_real and not compatible:
                conflicts.append((pid, iia, lab, ev[:70]))
            elif wrong_kind:
                conflicts.append((pid, iia, lab, ev[:70]))
    lab = re.sub(r"\b(\d{4}) \1\b", r"\1", lab).replace("&amp;", "&")
    out[pid] = {"venue": lab, "status": st, "evidence": ev}
json.dump(out, open(d + "/final.json", "w"), indent=1, ensure_ascii=False)
json.dump({"conflicts": conflicts, "unverified": unver}, open(d + "/review.json", "w"), indent=1, ensure_ascii=False)
c = collections.Counter(v["status"] for v in out.values())
print(c, "accepted-or-published:", c["published"] + c["accepted"])
print("conflicts:", len(conflicts)); [print("  ", *x) for x in conflicts]
print("unverified:", len(unver)); [print("  ", u, "|", P[u]["venue"], "|", P[u]["title"][:70]) for u in unver]
print("sample labels:", collections.Counter(v["venue"] for v in out.values() if v["status"] != "preprint").most_common(25))
