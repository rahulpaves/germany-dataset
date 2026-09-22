#!/usr/bin/env python3
"""Checks every number the site claims against germany-file.json.

Counts have drifted twice: once when records were removed and the hero kept the
old figure, once when a JS CONFIG value quietly overwrote a corrected one in the
markup. Run this before any deploy.

    python3 check_claims.py
"""
import os
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

import json as _j
_idx = _j.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "index.json")))
# Two kinds of country, and the headline may only count one of them.
#
# Eight were built programme by programme from each university's own pages, so
# every record was read by a person and the language of instruction is one of
# the things they checked. Those are the English-taught count.
#
# The UAE is the whole CAA National Register. It is far larger and it is the
# complete country rather than a verified subset, but the register does not
# publish language of instruction, so not one of those 1,792 rows has been
# confirmed English-taught. Adding them to the headline would turn a true
# sentence into a false one, which is the single thing this file exists to stop.
VERIFIED = [x for x in _idx if not x.get("depth")]
REGISTER = [x for x in _idx if x.get("depth") == "register"]
COMPILED = [x for x in _idx if x.get("depth") == "compiled"]
TOTAL_PROGRAMMES  = sum(x["programmes"] for x in VERIFIED)
REGISTER_PROGRAMMES = sum(x["programmes"] for x in REGISTER)
COMPILED_PROGRAMMES = sum(x["programmes"] for x in COMPILED)
print("multi-country: %d verified across %d countries, plus %d register rows and %d compiled rows\n"
      % (TOTAL_PROGRAMMES, len(VERIFIED), REGISTER_PROGRAMMES, COMPILED_PROGRAMMES))


checks = [
    ("hero headline",        r"<h1>(\d+) English-taught",                 TOTAL_PROGRAMMES),
    ("UAE register count",   r"(\d+) accredited UAE",                     REGISTER_PROGRAMMES),
    ("UK compiled count",    r"(\d+) UK undergraduate courses",           COMPILED_PROGRAMMES),
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
    (r"(\d+) English-taught",            None,                  "English-taught count"),
    (r"(\d+) fields on every programme", truth["min fields"],   "field floor"),
    (r"fields on every programme,? (?:and )?(\d+) on most",
                                          truth["most fields"],  "field typical"),
    (r"(\d+) German institutions",       truth["institutions"], "institution count"),
]:
    if want is None:
        print("  ok       %-22s multi-country, checked in the headline rule" % label); continue
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

# The chain step counts drift the moment a chain is rebuilt. "122 verified
# steps" outlived two rebuilds on the landing page before anyone noticed.
import glob as _glob
_steps = {}
_here = os.path.dirname(os.path.abspath(__file__))
# Paid countries moved to data-source/ when the gate went in; the chain
# totals still have to count them or the page claim goes stale silently.
for _f in (_glob.glob(os.path.join(_here, "data", "*-visa.json"))
           + _glob.glob(os.path.join(_here, "data-source", "*-visa.json"))):
    _c = os.path.basename(_f).replace("-visa.json", "")
    _v = json.load(open(_f))
    _steps[_c] = len(_v if isinstance(_v, list) else _v.get("steps", _v))
_total = sum(_steps.values())
print("  -- application chain steps --")
print("  data says: %d steps across %d countries (Germany %d)"
      % (_total, len(_steps), _steps.get("germany", 0)))
for _pat, _want, _label in [
    (r"(\d+) verified application and visa steps", _total,               "total steps"),
    (r"(\d+)-step application chain",              _steps.get("germany"), "Germany chain"),
]:
    _found = [int(m) for m in re.findall(_pat, html)]
    if not _found:
        print("  ok       %-22s not stated" % _label)
    elif any(f != _want for f in _found):
        print("  WRONG    %-22s says %s, data says %d"
              % (_label, sorted({f for f in _found if f != _want}), _want))
        bad += 1
    else:
        print("  ok       %-22s %d occurrence(s), all %d" % (_label, len(_found), _want))
print()

stale = re.findall(r"\b27 fields\b", html)
if stale:
    print("\n  WRONG    an old '27 fields' claim is still in the page"); bad += 1

links = sum(1 for r in d for f in ("url", "source_url_you_used")
            if not str(r.get(f) or "").startswith("http"))
if links:
    print("\n  WRONG    %d url/source values are not URLs" % links); bad += 1

# -- the change log ----------------------------------------------------------
# The subscription's renewal case is "the data stays current", and the change
# log is the evidence. A log that stops moving while the data keeps changing
# unsells that quietly, so the newest entry may not be older than the newest
# date_checked anywhere in the data.
_here = os.path.dirname(os.path.abspath(__file__))
try:
    _log = _j.load(open(os.path.join(_here, "data", "changelog.json")))
    _entry_dates = sorted(e["date"] for e in _log)
    _MON = {m: i + 1 for i, m in enumerate(
        ["January","February","March","April","May","June",
         "July","August","September","October","November","December"])}
    def _iso(text):
        m = re.match(r"(\d{1,2}) (\w+) (\d{4})", str(text).strip())
        if not m or m.group(2) not in _MON: return None
        return "%s-%02d-%02d" % (m.group(3), _MON[m.group(2)], int(m.group(1)))
    _checked = []
    import glob as _g
    for _p in _g.glob(os.path.join(_here, "data", "*.json")) + \
              _g.glob(os.path.join(_here, "data-source", "*.json")):
        if "changelog" in _p or "revoked" in _p: continue
        try: _rows = _j.load(open(_p))
        except Exception: continue
        if not isinstance(_rows, list): continue
        for _r in _rows:
            if isinstance(_r, dict):
                _d = _iso(_r.get("date_checked", ""))
                if _d: _checked.append(_d)
    if _checked and _entry_dates and max(_checked) > _entry_dates[-1]:
        print("  WRONG    data was checked on %s but the change log ends at %s"
              % (max(_checked), _entry_dates[-1])); bad += 1
    else:
        print("  ok       change log            newest entry %s covers newest check %s"
              % (_entry_dates[-1] if _entry_dates else "-", max(_checked) if _checked else "-"))
except FileNotFoundError:
    print("  WRONG    data/changelog.json is missing"); bad += 1

print()
if bad:
    print("RESULT: %d problem(s). Do not deploy." % bad); sys.exit(1)
print("RESULT: every number on the page matches the data.")
