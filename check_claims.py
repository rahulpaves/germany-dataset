#!/usr/bin/env python3
"""Checks every number the site claims against germany-file.json.

Counts have drifted twice: once when records were removed and the hero kept the
old figure, once when a JS CONFIG value quietly overwrote a corrected one in the
markup. Run this before any deploy.

    python3 check_claims.py
"""
import json, re, sys, pathlib

META = {"record_id", "verified_status", "corrected_value_if_any", "source_url_you_used",
        "exact_quote", "date_checked", "link_works", "checked_by"}

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
