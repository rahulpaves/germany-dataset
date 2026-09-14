# -*- coding: utf-8 -*-
"""Writes data/routes.json - the three-axis route model for all eight countries.

Axes are independent and each is keyed on what the official source actually
keys on:
  passport  - the visa route (what the immigration authority keys on)
  board     - the qualification (what the recognition body keys on)
  residence - where the student applies FROM (which mission, which attestation)

Getting these wrong is the whole point of the rebuild: APS is keyed on the
board, Etudes en France on residence, the MVV on the passport. Collapsing them
into one "Indian student" tag made all three wrong for the same student.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from routes_src import (EU_EEA, SG_VISA_REQUIRED, NL_MVV_EXEMPT, EEF_COUNTRIES,
                        DE_B, DE_C, DE_D, BOARDS)

D = "14 September 2026"
OTHER = "Other (non-EU)"
INDIAN = ["cbse", "isc", "state"]
NON_INDIAN = ["ib", "alevel", "us"]
ALL_B = INDIAN + NON_INDIAN

# One country universe for every destination. Germany's tiers were only ever a
# partition OF this list, so drawing from DE_D alone silently dropped China,
# India, Mongolia and Vietnam from every other country's picker.
WORLD = sorted(set(EU_EEA + DE_B + DE_C + DE_D) - {OTHER}) + [OTHER]
NON_EU = [c for c in WORLD if c not in EU_EEA]

def rest(*exclude):
    """Every non-EU passport that isn't already named in an earlier tier."""
    seen = set()
    for grp in exclude:
        seen |= set(grp)
    return [c for c in NON_EU if c not in seen]

def tier(id, name, summary, countries, source_url=None, quote=None):
    t = {"id": id, "name": name, "summary": summary, "countries": countries}
    if source_url: t["source_url"] = source_url
    if quote: t["exact_quote"] = quote
    return t

R = {}

# ---------------------------------------------------------------- GERMANY ----
# Correction, 14 Sep 2026: APS was tiered by nationality. It is not - the APS
# India FAQ keys it on the issuing institution. It moves to the board axis.
R["germany"] = {
 "passport": {"label": "Passport", "default": "c", "tiers": [
   tier("a", "EU / EEA / Switzerland", "No visa and no residence permit. Enrol, arrange health insurance, and register the address within two weeks of arrival.", EU_EEA),
   tier("b", "Visa-free entry, permit obtained inside Germany", "No visa needed to enter. The student travels first, then applies for the residence permit inside Germany within 90 days. This skips the embassy appointment entirely.", DE_B),
   tier("c", "National (Type D) student visa", "A full Type D student visa before travel. The variable that matters most is appointment availability at the student's local German mission.", sorted(set(DE_C + DE_D)))]},
 "board": {"label": "Curriculum", "default": "cbse", "notes": {
   "cbse": "APS applies: the certificate is issued by an Indian board. From WS 2026/27 the anabin criteria also require <b>70% of the maximum achievable marks</b> in Class XII before any German university will assess the file.",
   "isc": "APS applies: the certificate is issued by an Indian board. The 70% Class XII floor from WS 2026/27 applies here too.",
   "state": "APS applies, and state boards are the most likely to need an individual anabin check. The 70% Class XII floor applies.",
   "ib": "<b>No APS.</b> The IB Diploma is not issued by an Indian institution, so an Indian passport holder with an IB Diploma falls outside APS India's remit. The 70% Class XII floor does not apply either.",
   "alevel": "<b>No APS.</b> Cambridge A Levels are not issued by an Indian institution. Direct entry normally needs three A Levels; check anabin for the specific combination.",
   "us": "<b>No APS.</b> A US high school diploma alone rarely gives direct entry - it usually needs AP subjects or a year of university, otherwise the student is on a Studienkolleg year."}},
 "residence": {"label": "Applying from", "default": "other", "options": [
   {"id":"in","name":"India","note":"APS India, New Delhi. The visa file goes through the Consular Services Portal first; the VFS appointment link only appears at the end of a completed application. Remonstration has been abolished in India since 1 January 2024, so the first submission is the only one."},
   {"id":"ae","name":"UAE","note":"The German missions in Abu Dhabi and Dubai, through the UAE VFS centres. A student on a CBSE or ISC certificate still falls under APS India even though the school is in the UAE, because the board is Indian - confirm with APS India before assuming either way."},
   {"id":"other","name":"Somewhere else","note":""}]}}

# ------------------------------------------------------------ NETHERLANDS ----
R["netherlands"] = {
 "passport": {"label": "Passport", "default": "c", "tiers": [
   tier("a", "EU / EEA / Switzerland", "Free movement. No MVV, no residence permit, no TB test. Register with the municipality after arrival.", EU_EEA),
   tier("b", "MVV-exempt", "No entry visa needed, but the student still needs a VVR residence permit. The university applies for it; the student collects it in the Netherlands rather than at a consulate.", NL_MVV_EXEMPT,
        "https://ind.nl/en/mvv-exemptions",
        "Your nationality determines whether you need an MVV. You do not need an MVV if you have the nationality of one of these countries."),
   tier("c", "MVV required", "The university runs the TEV procedure - entry visa and residence permit applied for together. The student collects the MVV sticker at a Dutch mission before travelling.", rest(NL_MVV_EXEMPT),
        "https://ind.nl/en/mvv-exemptions",
        "Your nationality determines whether you need an MVV.")]},
 "board": {"label": "Curriculum", "default": "cbse", "notes": {
   "cbse":"Standard XII is weighed against HAVO/VWO. Several universities accept only CBSE and CISCE and will not look at a state board, and many require a first year of Indian university on top.",
   "isc":"Treated alongside CBSE by the universities that publish a country rule; the same HAVO/VWO comparison applies.",
   "state":"The weakest position. Check each university's country page - a number of them accept only CBSE and CISCE.",
   "ib":"Direct entry at every Dutch research university. No foundation year, no first-year-of-university condition.",
   "alevel":"Direct entry, normally on three A Levels. Subject requirements are programme-specific.",
   "us":"A diploma alone is usually not enough for a research university - AP subjects or a year of college is the normal condition."}},
 "residence": {"label": "Applying from", "default": "other", "options": [
   {"id":"in","name":"India","note":"Documents need an apostille from the Ministry of External Affairs. The MVV sticker is collected at New Delhi, Mumbai or Bengaluru within a three-month window."},
   {"id":"ae","name":"UAE","note":"Documents are attested through the UAE Ministry of Foreign Affairs rather than the Indian MEA chain. The MVV is collected at the Dutch mission in Abu Dhabi or Dubai."},
   {"id":"other","name":"Somewhere else","note":""}]}}

# ----------------------------------------------------------------- FRANCE ----
R["france"] = {
 "passport": {"label": "Passport", "default": "b", "tiers": [
   tier("a", "EU / EEA / Switzerland", "No visa and no residence permit. Enrol and arrange health cover; nothing in the visa chain applies.", EU_EEA),
   tier("b", "Non-EU", "A VLS-TS long-stay student visa, validated online within three months of arrival. Whether the file runs through Etudes en France depends on where the student lives, not on the passport.", rest())]},
 "board": {"label": "Curriculum", "default": "cbse", "notes": {
   "cbse":"There is no French APS or anabin. Class XII is assessed by the institution itself, so the bar differs school by school.",
   "isc":"Assessed by the institution; no central recognition step.",
   "state":"Assessed by the institution; expect more scrutiny than CBSE or ISC.",
   "ib":"Widely recognised for direct entry, including at the grandes ecoles.",
   "alevel":"Recognised for direct entry; subject combination matters more than the grades at most institutions.",
   "us":"Usually needs AP subjects or SAT alongside the diploma."}},
 "residence": {"label": "Applying from", "default": "eef", "options": [
   {"id":"eef","name":"A country covered by Etudes en France","note":"The Etudes en France procedure is <b>compulsory</b> and it is keyed on where the student lives, not the passport. It applies even at the private grandes ecoles: the school can admit the student directly, but without an EEF file there is no visa. 73 countries are covered, India and the UAE among them.",
    "countries": EEF_COUNTRIES,
    "source_url":"https://www.campusfrance.org/en/faq/which-countries-are-affected-by-the-etudes-en-france-studying-in-france-procedure",
    "exact_quote":"Students who reside in one of the countries affected by this procedure must make a specific request for enrolment."},
   {"id":"in","name":"India (Etudes en France)","note":"Campus France India. The EEF fee rose from INR 18,500 to INR 20,000, and the academic interview is held in India.",
    "source_url":"https://www.inde.campusfrance.org/etudes-en-france-studying-in-france-procedure-calendar"},
   {"id":"ae","name":"UAE (Etudes en France)","note":"Campus France UAE, not Campus France India - the procedure follows residence. An Indian passport holder living in Dubai files through the UAE office and pays the UAE fee, and the interview is held there."},
   {"id":"other","name":"A country not covered","note":"No Etudes en France file. The student applies to the institution directly and then to the French consulate for the VLS-TS."}]}}

# ------------------------------------------------------------------ ITALY ----
R["italy"] = {
 "passport": {"label": "Passport", "default": "b", "tiers": [
   tier("a", "EU / EEA / Switzerland", "No visa, no pre-enrolment quota, no Universitaly step. Apply to the university directly and enrol.", EU_EEA),
   tier("b", "Non-EU residing abroad", "Universitaly pre-enrolment is mandatory and the student competes inside the reserved non-EU quota for the programme. Type D study visa before travel, then a permesso di soggiorno within 8 working days of landing.", rest())]},
 "board": {"label": "Curriculum", "default": "cbse", "notes": {
   "cbse":"Class XII clears the 12-years-of-schooling bar on its own. Recognition runs either through a CIMEA statement or a consular Declaration of Value.",
   "isc":"Same as CBSE - 12 years of schooling is satisfied, then CIMEA or a Declaration of Value.",
   "state":"12 years is satisfied, but expect the consulate to scrutinise a state board record more closely.",
   "ib":"The IB Diploma is recognised directly and CIMEA processes it quickly; no Declaration of Value is normally needed.",
   "alevel":"Recognised, but Italy counts years of schooling - a student with fewer than 12 years may need a supplementary year or university credits.",
   "us":"A US diploma is 12 years and is accepted, though some universities ask for AP subjects."}},
 "residence": {"label": "Applying from", "default": "other", "options": [
   {"id":"in","name":"India","note":"The Indian attestation chain applies: HRD attestation first, then MEA apostille, before the Declaration of Value at the competent Italian consulate."},
   {"id":"ae","name":"UAE","note":"Attestation runs through the UAE Ministry of Foreign Affairs, and the Declaration of Value is issued by the Italian consulate in Dubai or the embassy in Abu Dhabi - not by the Indian posts."},
   {"id":"other","name":"Somewhere else","note":""}]}}

# ------------------------------------------------------------------ SPAIN ----
R["spain"] = {
 "passport": {"label": "Passport", "default": "b", "tiers": [
   tier("a", "EU / EEA / Switzerland", "No student visa. The academic route (homologacion or UNEDasiss) still applies, because that is keyed on the qualification, not the passport.", EU_EEA),
   tier("b", "Non-EU", "A student visa before travel, then a TIE card after arrival. The academic route runs in parallel and is the longer of the two.", rest())]},
 "board": {"label": "Curriculum", "default": "cbse", "notes": {
   "cbse":"Homologacion of Class XII is the single biggest scheduling risk in the whole Spanish chain - it gates the public-university route and routinely takes months.",
   "isc":"Same homologacion route and the same waiting time as CBSE.",
   "state":"Same route; sworn translation of a state board record takes longer to arrange.",
   "ib":"UNEDasiss accepts the IB Diploma directly and homologacion is generally not required for the public route - this removes the longest wait in the chain.",
   "alevel":"UNEDasiss handles A Levels through its own accreditation route; check which PCE subjects the target degree needs.",
   "us":"Handled through UNEDasiss; a US diploma normally needs PCE subject exams to compete for a public place."}},
 "residence": {"label": "Applying from", "default": "other", "options": [
   {"id":"in","name":"India","note":"Apostille and sworn translation of the school record, and a Police Clearance Certificate from the Regional Passport Office. There is no PCE exam centre in India, which is its own scheduling problem."},
   {"id":"ae","name":"UAE","note":"UAE MOFA attestation rather than the Indian apostille chain, and the police certificate comes from the UAE authorities. Confirm the nearest PCE exam centre before booking anything."},
   {"id":"other","name":"Somewhere else","note":""}]}}

# ------------------------------------------------------------ SWITZERLAND ----
R["switzerland"] = {
 "passport": {"label": "Passport", "default": "b", "tiers": [
   tier("a", "EU / EFTA", "Free movement under the AFMP. Enter without a visa, then register with the commune within 14 days and apply for a B permit for study.", EU_EEA),
   tier("b", "Third-country national", "A national D visa applied for in person at the Swiss representation in the country of residence, then registration with the commune within 14 days and a cantonal B permit.", rest())]},
 "board": {"label": "Curriculum", "default": "cbse", "notes": {
   "cbse":"The swissuniversities country table is the gate, and for India it is restrictive - Class XII alone is generally not admissible for direct entry at HSG. Read the table before anything else.",
   "isc":"Same swissuniversities country table and the same restriction as CBSE.",
   "state":"Same table; a state board record is the least likely to clear direct entry.",
   "ib":"Admissible for direct entry - this is the realistic route into Swiss universities for a student in an international school.",
   "alevel":"Admissible for direct entry, subject to the subject combination the university requires.",
   "us":"A diploma alone is normally not admissible; APs or a year of university are usually required."}},
 "residence": {"label": "Applying from", "default": "other", "options": [
   {"id":"in","name":"India","note":"The D visa is lodged in person at the Swiss Embassy in New Delhi. Its checklist makes IELTS or TOEFL mandatory even where the university itself does not ask for one - HSG says no language proof is needed and the embassy checklist disagrees."},
   {"id":"ae","name":"UAE","note":"The D visa is lodged at the Swiss Embassy in Abu Dhabi. Check its own document checklist - the New Delhi language-proof rule is a New Delhi rule, not a Swiss-wide one."},
   {"id":"other","name":"Somewhere else","note":""}]}}

# -------------------------------------------------------------- SINGAPORE ----
R["singapore"] = {
 "passport": {"label": "Passport", "default": "b", "tiers": [
   tier("a", "Student's Pass only", "A Student's Pass through SOLAR and ICA. No separate entry visa - the IPA letter is enough to travel.", [c for c in WORLD if c not in SG_VISA_REQUIRED],
        "https://www.ica.gov.sg/enter-transit-depart/entering-singapore/visa_requirements",
        "Nationals of the listed countries require a visa to enter Singapore."),
   tier("b", "Student's Pass and an entry visa", "A Student's Pass plus an entry visa. The IPA letter doubles as the single-journey entry visa, and ICA takes about two weeks rather than one because of it.", SG_VISA_REQUIRED,
        "https://www.ica.gov.sg/enter-transit-depart/entering-singapore/visa_requirements",
        "Nationals of the listed countries require a visa to enter Singapore.")]},
 "board": {"label": "Curriculum", "default": "cbse", "notes": {
   "cbse":"Direct entry - Class XII needs no equivalence and no foundation year. NUS and NTU publish completely different thresholds, so read each one rather than a single 'Indian cutoff'.",
   "isc":"Direct entry on the same basis as CBSE.",
   "state":"Direct entry, though the published indicative grade profiles are built on CBSE and ISC records.",
   "ib":"Direct entry. NUS does not publish IB grade profiles at all, so there is no cutoff to quote - only the subject prerequisites.",
   "alevel":"Direct entry. The published indicative grade profiles for Singapore-Cambridge A Levels are the clearest numbers either university releases.",
   "us":"Accepted with SAT or AP alongside the diploma."}},
 "residence": {"label": "Applying from", "default": "other", "options": [
   {"id":"in","name":"India","note":"Nothing India-specific in the application itself. The entry visa follows the passport, not the address - an Indian passport needs one wherever the student lives."},
   {"id":"ae","name":"UAE","note":"A UAE residence address does not change the entry-visa position, which follows the passport. A temporary UAE passport does require a visa; a normal one does not."},
   {"id":"other","name":"Somewhere else","note":""}]}}

# -------------------------------------------------------------- AUSTRALIA ----
R["australia"] = {
 "passport": {"label": "Passport", "default": "b", "tiers": [
   tier("a", "New Zealand citizen", "No student visa. A New Zealand citizen can study on a Special Category visa granted on arrival, though fees are charged at the international rate unless residency tests are met.", ["New Zealand"]),
   tier("b", "All other non-citizens", "A subclass 500 student visa, with the Genuine Student requirement, OSHC for the whole visa period, and the AUD 2,500 application charge.", [c for c in WORLD if c != "New Zealand"])]},
 "board": {"label": "Curriculum", "default": "cbse", "notes": {
   "cbse":"A recognised qualification at every Go8 university, but each one converts it on a different scale - percentages, best-four aggregates, 20-point scales. A single 'Indian cutoff' is wrong nearly everywhere.",
   "isc":"Recognised on the same basis; conversion differs by university exactly as it does for CBSE.",
   "state":"Recognised, but several universities apply a lower conversion to state boards than to CBSE and ISC.",
   "ib":"Converted through a published IB-to-ATAR table, which makes it the most predictable route for entry scores.",
   "alevel":"Converted through a published A-Level-to-ATAR table; the best three or four subjects are counted depending on the university.",
   "us":"Usually needs SAT or AP alongside the diploma to generate a comparable rank."}},
 "residence": {"label": "Applying from", "default": "other", "options": [
   {"id":"in","name":"India","note":"India sits in a higher evidence tier at most providers, which means the financial-capacity and Genuine Student evidence is read more strictly than the published minimum suggests."},
   {"id":"ae","name":"UAE","note":"Evidence level is set by the passport and the provider together, not by the UAE address. An Indian passport holder in Dubai is generally assessed on the Indian evidence level."},
   {"id":"other","name":"Somewhere else","note":""}]}}

for c in R:
    R[c]["boards"] = BOARDS
    R[c]["date_checked"] = D
R["_meta"] = {"built": D, "axes": ["passport", "board", "residence"],
  "note": "Each axis is keyed on what the official source keys on. APS follows the board, Etudes en France follows residence, the MVV follows the passport."}

out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "routes.json")
json.dump(R, open(out, "w"), indent=1, ensure_ascii=False)
print("wrote", out)
for c in sorted(k for k in R if not k.startswith("_")):
    p = R[c]["passport"]["tiers"]
    src = sum(1 for t in p if t.get("source_url"))
    print(f"  {c:12} {len(p)} passport tiers ({src} sourced) | "
          f"{len(R[c]['board']['notes'])} board notes | {len(R[c]['residence']['options'])} residences")
