#!/usr/bin/env python3
"""Checks every number the site claims against germany-file.json.

Counts have drifted twice: once when records were removed and the hero kept the
old figure, once when a JS CONFIG value quietly overwrote a corrected one in the
markup. Run this before any deploy.

    python3 check_claims.py
"""
import json, re, sys, pathlib

# deadline_iso is derived from deadline so the page can tell a passed intake
# from a live one. It is plumbing, not something a counselor reads.
META = {"record_id", "verified_status", "corrected_value_if_any", "source_url_you_used",
        "exact_quote", "date_checked", "link_works", "checked_by", "deadline_iso"}

d = json.load(open("germany-file.json"))
html = pathlib.Path("index.html").read_text()

keys = {k for r in d for k in r if k not in META}
fills = sorted(sum(1 for k in keys if str(r.get(k) or "").strip()) for r in d)
truth = {
    "programmes":   len(d),
    "institutions": len({r["institution"] for r in d}),
    "min fields":   fills[0],
    "most fields":  max(set(fills), key=fills.count),
}

checks = [
    ("hero headline",        r"<h1>(\d+) English-taught",                 truth["programmes"]),
    ("PROGRAMME_COUNT",      r"PROGRAMME_COUNT:\s*(\d+)",                 truth["programmes"]),
    ("UNI_COUNT",            r"UNI_COUNT:\s*(\d+)",                       truth["institutions"]),
    ("Germany picker progs", r'"Germany":\[(\d+),\d+\]',                  truth["programmes"]),
    ("Germany picker unis",  r'"Germany":\[\d+,(\d+)\]',                  truth["institutions"]),
    ("coverCount",           r'id="coverCount">(\d+)<',                   truth["programmes"]),
    ("coverUnis",            r'id="coverUnis">(\d+)<',                    truth["institutions"]),
    ("progCountTag",         r'id="progCountTag">(\d+)<',                 truth["programmes"]),
    ("wygCount",             r'id="wygCount">(\d+)<',                     truth["programmes"]),
    ("hero field floor",     r"<strong>(\d+) fields on every programme",  truth["min fields"]),
    ("hero field typical",   r"fields on every programme, (\d+) on most", truth["most fields"]),
]

print("data says: %d programmes, %d institutions, %d fields minimum, %d typical\n"
      % (truth["programmes"], truth["institutions"], truth["min fields"], truth["most fields"]))

bad = 0
for label, pat, want in checks:
    m = re.search(pat, html)
    if not m:
        print("  MISSING  %-22s pattern not found" % label); bad += 1
    elif int(m.group(1)) != want:
        print("  WRONG    %-22s page says %s, data says %s" % (label, m.group(1), want)); bad += 1
    else:
        print("  ok       %-22s %s" % (label, m.group(1)))

# The subject breakdown on the hero drifts every time programmes are added,
# and it drifted badly once: the list still said Engineering 1 after five
# engineering programmes had landed. Derive it from the data instead.
OVERRIDE = {
    "Aerospace (BSc)": "Engineering",
    "Robotics and Intelligent Systems (BSc)": "Engineering",
    "Bioengineering": "Engineering",
    "Software Engineering (BSc)": "Computer science, data & software",
    "Software Engineering (BSc Hons)": "Computer science, data & software",
    "North American Studies (BA)": "Humanities & social sciences",
    "Humanities, The Arts and Social Thought (BA)": "Humanities & social sciences",
    "Liberal Arts and Sciences (BSc - English)": "Humanities & social sciences",
    "Agribusiness": "Business, management & economics",
}

def subject_of(programme):
    if programme in OVERRIDE:
        return OVERRIDE[programme]
    t = programme.lower()
    if re.search(r"engineer|mechatronic|infotronic|mobility and logistics|environment and energy", t):
        return "Engineering"
    if re.search(r"computer|informatic|software|data science|artificial intelligence|comput", t):
        return "Computer science, data & software"
    if re.search(r"biolog|life science|chemistr|physic|material|agricultur|agribusiness|biomed|mathemat", t):
        return "Natural & life sciences"
    if re.search(r"design|architect|media|advertis|art", t):
        return "Design, architecture & media"
    if re.search(r"business|management|economic|finance|account|marketing|taxation|tourism|commerce|logistic", t):
        return "Business, management & economics"
    return "Humanities & social sciences"

counts = {}
for r in d:
    k = subject_of(r.get("programme", ""))
    counts[k] = counts.get(k, 0) + 1

print("  -- subject breakdown on the hero --")
listed = 0
for subject, want in sorted(counts.items(), key=lambda kv: -kv[1]):
    pat = r"<li><span>%s</span><b>(\d+)</b></li>" % re.escape(subject.replace("&", "&amp;"))
    m = re.search(pat, html)
    if not m:
        print("  MISSING  %-34s not listed, data says %d" % (subject, want)); bad += 1
    elif int(m.group(1)) != want:
        print("  WRONG    %-34s page says %s, data says %d" % (subject, m.group(1), want)); bad += 1
    else:
        print("  ok       %-34s %d" % (subject, want)); listed += int(m.group(1))

if listed and listed != truth["programmes"]:
    print("  WRONG    subject counts total %d, data has %d" % (listed, truth["programmes"])); bad += 1
print()

# Numbers repeat in meta tags, the hero and the body copy. Checking one selector
# let "29 fields" survive in two og/twitter tags after the visible copy was fixed,
# which is what a counselor sees when the link is shared. Sweep every occurrence.
print("  -- every numeric claim in the page --")
for pat, want, label in [
    (r"(\d+) English-taught",            truth["programmes"],   "English-taught count"),
    (r"(\d+) fields on every programme", truth["min fields"],   "field floor"),
    (r"fields on every programme,? (?:and )?(\d+) on most",
                                          truth["most fields"],  "field typical"),
    (r"(\d+) German institutions",       truth["institutions"], "institution count"),
]:
    found = [int(m) for m in re.findall(pat, html)]
    if not found:
        print("  ok       %-22s not stated" % label)
    elif any(f != want for f in found):
        wrong = sorted({f for f in found if f != want})
        print("  WRONG    %-22s %s occurrence(s) say %s, data says %d"
              % (label, sum(1 for f in found if f != want), wrong, want))
        bad += 1
    else:
        print("  ok       %-22s %d occurrence(s), all %d" % (label, len(found), want))
print()

stale = re.findall(r"\b27 fields\b", html)
if stale:
    print("\n  WRONG    an old '27 fields' claim is still in the page"); bad += 1

links = sum(1 for r in d for f in ("url", "source_url_you_used")
            if not str(r.get(f) or "").startswith("http"))
if links:
    print("\n  WRONG    %d url/source values are not URLs" % links); bad += 1

print()
if bad:
    print("RESULT: %d problem(s). Do not deploy." % bad); sys.exit(1)
print("RESULT: every number on the page matches the data.")
