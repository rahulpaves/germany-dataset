# -*- coding: utf-8 -*-
"""Re-tag every chain step onto three independent axes.

Before: one "who" tag doing the work of all three, so "india" meant passport,
board and residence at once. Splitting it is the fix.

An EMPTY axis list means "applies to everyone" - only genuine conditions are
listed. Each entry below is keyed by a distinctive substring of the step title
so it survives step renumbering.
"""
import json, glob, os, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "data")
IND = ["cbse", "isc", "state"]
ALLB = IND + ["ib", "alevel", "us"]

# (country, title substring) -> {passport: [...], board: [...], residence: [...]}
RULES = {
 # ---- AUSTRALIA -----------------------------------------------------------
 ("australia","Indian Standard XII board is a recognised"): {"board": IND},
 # ---- FRANCE --------------------------------------------------------------
 ("france","CBSE/ISC Class XII recognition"):               {"board": IND},
 ("france","Open the Etudes en France"):                    {"passport":["b"], "residence":["eef","in","ae"]},
 ("france","Pay the Etudes en France fee"):                 {"passport":["b"], "residence":["in"]},
 ("france","Campus France academic interview in India"):    {"passport":["b"], "residence":["in"]},
 ("france","EU/EEA/Swiss shortcut"):                        {"passport":["a"]},
 # ---- GERMANY -------------------------------------------------------------
 ("germany","70 percent Class XII floor"):                  {"board": IND},
 ("germany","APS certificate"):                             {"board": IND},
 ("germany","dMAT for Indian Master"):                      {"board": IND},
 ("germany","TestAS only if"):                              {"passport":["b","c"]},
 ("germany","Blocked account"):                             {"passport":["b","c"]},
 ("germany","Consular Services Porta"):                     {"passport":["c"]},
 ("germany","on-site appointment (VFS)"):                   {"passport":["c"]},
 ("germany","Visa processing and the decision"):            {"passport":["c"]},
 ("germany","Entry/Exit System (EES)"):                     {"passport":["b"]},
 ("germany","Convert to a residence permit"):               {"passport":["b","c"]},
 # ---- ITALY ---------------------------------------------------------------
 ("italy","12-years-of-schooling bar"):                     {"board": IND},
 ("italy","Indian attestation chain"):                      {"passport":["b"], "residence":["in"]},
 ("italy","Declaration of Value at the competent"):         {"passport":["b"]},
 ("italy","EU/EEA shortcut"):                               {"passport":["a"]},
 # ---- NETHERLANDS ---------------------------------------------------------
 ("netherlands","Standard XII is actually worth"):          {"board": IND},
 ("netherlands","university's own country rule"):           {"board": IND},
 ("netherlands","apostilled by the Ministry of External"):  {"passport":["b","c"], "residence":["in"]},
 ("netherlands","TB declaration of intent"):                {"passport":["c"]},
 ("netherlands","Collect the MVV sticker in India"):        {"passport":["c"], "residence":["in"]},
 ("netherlands","TB test at the GGD"):                      {"passport":["c"]},
 # ---- SINGAPORE -----------------------------------------------------------
 ("singapore","Indian Standard XII needs no equivalence"):  {"board": IND},
 ("singapore","real academic bar"):                         {"board": IND},
 ("singapore","Class 11 / predicted results"):              {"board": IND},
 ("singapore","IPA letter"):                                {"passport":["b"]},
 # ---- SPAIN ---------------------------------------------------------------
 # homologacion is keyed on the QUALIFICATION, not the passport - it applied to
 # IB and A-Level students too and was wrongly hidden from them.
 ("spain","sworn-translate the school record"):             {"board": IND, "residence":["in"]},
 ("spain","File the homologación application"):             {"board": IND},
 ("spain","Wait out the homologación decision"):            {"board": IND},
 ("spain","Police Clearance Certificate"):                  {"passport":["b"], "residence":["in"]},
 # ---- SWITZERLAND ---------------------------------------------------------
 ("switzerland","swissuniversities country table"):         {"board": IND},
 ("switzerland","Take IELTS or TOEFL anyway"):              {"passport":["b"], "residence":["in"]},
 ("switzerland","Swiss Embassy in New Delhi"):              {"passport":["b"], "residence":["in"]},
}

# Steps whose OLD tag was purely a visa-route condition map straight across.
LEGACY_PASSPORT = {"eu_eea": ["a"], "intl": None, "india": None}

def axes_for(country, title, old):
    for (c, frag), ax in RULES.items():
        if c == country and frag.lower() in title.lower():
            return dict(ax), True
    return {}, False

def main():
    total = matched = 0
    report = collections.defaultdict(list)
    for f in sorted(glob.glob(os.path.join(DATA, "*-visa.json"))):
        country = os.path.basename(f).replace("-visa.json", "")
        d = json.load(open(f))
        arr = d if isinstance(d, list) else d.get("steps", d)
        for s in arr:
            total += 1
            title = s.get("title") or ""
            ax, hit = axes_for(country, title, s.get("who"))
            if hit:
                matched += 1
                report[country].append((title[:58], ax))
            s["axes"] = {"passport": ax.get("passport", []),
                         "board":    ax.get("board", []),
                         "residence":ax.get("residence", [])}
            s.pop("who", None)
        json.dump(d, open(f, "w"), indent=1, ensure_ascii=False)
    print(f"{total} steps re-tagged | {matched} carry a real condition | "
          f"{total-matched} apply to everyone\n")
    for c in sorted(report):
        print(c.upper())
        for t, ax in report[c]:
            bits = " ".join(f"{k}={','.join(v)}" for k, v in ax.items() if v)
            print(f"   {t:58} {bits}")
        print()

main()
