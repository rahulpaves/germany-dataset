# -*- coding: utf-8 -*-
"""Structural gate on the three-axis route model. Non-zero exit = do not ship.

Catches the class of bug that shipped once already: a tier list built from the
wrong universe, so India silently vanished from six countries' pickers.
"""
import json, glob, os, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "data")
R = json.load(open(os.path.join(DATA, "routes.json")))
bad = 0
def wrong(m):
    global bad; print("  WRONG   ", m); bad += 1

MUST_HAVE = ["India", "China", "United Arab Emirates", "Pakistan", "United Kingdom",
             "United States", "Germany", "Nigeria", "Egypt", "Other (non-EU)"]

for c in sorted(k for k in R if not k.startswith("_")):
    cr = R[c]
    tiers = cr["passport"]["tiers"]
    ids = [t["id"] for t in tiers]
    if len(set(ids)) != len(ids): wrong(f"{c}: duplicate tier ids {ids}")

    seen = collections.Counter()
    for t in tiers:
        if not t.get("countries"): wrong(f"{c}/{t['id']}: tier has no countries")
        seen.update(t["countries"])
    twice = [k for k, v in seen.items() if v > 1]
    if twice: wrong(f"{c}: passport in more than one tier: {twice[:6]}")
    for m in MUST_HAVE:
        if m not in seen: wrong(f"{c}: '{m}' missing from every passport tier")
    if cr["passport"].get("default") not in ids:
        wrong(f"{c}: passport default '{cr['passport'].get('default')}' is not a tier")

    board_ids = [b["id"] for b in cr["boards"]]
    for b in cr["board"]["notes"]:
        if b not in board_ids: wrong(f"{c}: board note for unknown board '{b}'")
    for b in board_ids:
        if b not in cr["board"]["notes"]: wrong(f"{c}: board '{b}' has no note")
    res_ids = [o["id"] for o in cr["residence"]["options"]]
    if cr["residence"].get("default") not in res_ids:
        wrong(f"{c}: residence default is not an option")

    # every axis value a step names must exist in the model
    f = os.path.join(DATA, c + "-visa.json")
    d = json.load(open(f)); arr = d if isinstance(d, list) else d.get("steps", d)
    cond = 0
    for s in arr:
        a = s.get("axes")
        if a is None: wrong(f"{c}: step '{(s.get('title') or '')[:40]}' has no axes"); continue
        if a["passport"] or a["board"] or a["residence"]: cond += 1
        for v in a["passport"]:
            if v not in ids: wrong(f"{c}: step names unknown tier '{v}'")
        for v in a["board"]:
            if v not in board_ids: wrong(f"{c}: step names unknown board '{v}'")
        for v in a["residence"]:
            if v not in res_ids: wrong(f"{c}: step names unknown residence '{v}'")
    # a tier that hides nothing, or hides everything, is a modelling error
    for t in ids:
        n = sum(1 for s in arr if not s["axes"]["passport"] or t in s["axes"]["passport"])
        if n == 0: wrong(f"{c}/{t}: shows zero steps")
        if n < 3: wrong(f"{c}/{t}: shows only {n} steps - check the tagging")
    print(f"  {c:12} {len(tiers)} tiers, {len(seen)} passports, {len(arr)} steps, {cond} conditional")

print()
if bad: print(f"RESULT: {bad} problem(s). Do not ship."); sys.exit(1)
print("RESULT: route model is structurally sound.")
