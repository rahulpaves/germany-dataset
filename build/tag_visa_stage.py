# -*- coding: utf-8 -*-
"""Second tagging pass: steps a free-movement passport genuinely skips.

The first pass only touched steps that already carried a non-universal tag.
Everything else was "india intl" - both non-EU tracks - so the EU case was
never modelled at all. With a real EU/EFTA tier the gap shows: an EU student
was still being shown the permesso di soggiorno.

Conservative on purpose: a step is only narrowed when its SUBSTANCE is the
visa or the permit. Enrolment, housing, tuition and registration stay universal
because they apply to everyone. Under-filtering is the safe error here.
"""
import json, glob, os, sys

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

NONEU = {  # country -> (tier ids that are NOT free-movement, [title fragments])
 "australia": (["b"], [
   "financial capacity file","annual income route","Buy OSHC","visa application charge",
   "ImmiAccount and run the Document","Genuine Student (GS) answers","GS evidence pack",
   "health examinations","Time the lodgement date","Lodge the subclass 500",
   "Give biometrics","Processing - understand both","Grant: check the visa end date",
   "not before the OSHC start date","post-study step"]),
 "france": (["b"], [
   "proof-of-funds file at the NEW threshold","File the VLS-TS application",
   "Visa processing - budget 2 to 3 months","Validate the VLS-TS online",
   "convert the VLS-TS into a carte de sejour"]),
 "italy": (["b"], [
   "Build the proof of funds","Lock accommodation that the consulate",
   "Book the visa appointment","Submit the type D","what the visa does and does not",
   "permesso di soggiorno within 8","Questura appointment","Plan the first renewal"]),
 "netherlands": (["b","c"], [
   "IND recognised sponsor","files the MVV and residence permit",
   "Collect the residence permit card","Meet the IND study norm",
   "Transfer tuition AND the living-cost","Stay compliant: 50%"]),
 "spain": (["b"], [
   "Prove financial means at 100% of IPREM","insurer authorised to operate in Spain",
   "medical certificate under the 2005","Book the BLS appointment",
   "Wait for the decision - one month by law","2025 Reglamento gave you",
   "Apply for the TIE within one month","Work rights: up to 30 hours",
   "After graduation"]),
 "switzerland": (["b"], [
   "proof of funds to the Canton","two-authority structure","Collect the D visa and travel",
   "Work rights: nothing for the first six months"]),
}

changed = 0
for c, (tiers, frags) in NONEU.items():
    f = os.path.join(DATA, c + "-visa.json")
    d = json.load(open(f)); arr = d if isinstance(d, list) else d.get("steps", d)
    hit = []
    for s in arr:
        t = s.get("title") or ""
        if s["axes"]["passport"]:
            continue                      # a manual rule already decided this one
        for fr in frags:
            if fr.lower() in t.lower():
                s["axes"]["passport"] = list(tiers)
                hit.append(t[:62]); changed += 1
                break
    json.dump(d, open(f, "w"), indent=1, ensure_ascii=False)
    missed = [fr for fr in frags if not any(fr.lower() in (s.get("title") or "").lower() for s in arr)]
    print(f"{c:12} narrowed {len(hit):2} steps to passport={'/'.join(tiers)}" +
          (f"   UNMATCHED: {missed}" if missed else ""))
print(f"\n{changed} steps narrowed")
