# -*- coding: utf-8 -*-
"""Bring index.html's sample in line with the three-axis model.

Three claims on the landing page were stale or wrong:
  - "nine-step visa chain"  -> Germany's chain is 21 steps
  - "122 verified steps"    -> 184 across eight countries
  - APS presented as a nationality tier. The APS India FAQ keys it on the
    issuing institution, so it belongs to the curriculum, not the passport.
"""
import io, os, sys
F = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "index.html")
s = io.open(F, encoding="utf-8").read(); orig = s
def sub(a, b, label, cnt=1):
    global s
    if a not in s: sys.exit("PATCH FAILED: " + label)
    n = s.count(a)
    s = s.replace(a, b, cnt); print(f"  patched: {label}" + (f" ({n} occurrence(s))" if n > 1 else ""))

sub("Same TUM degree: an Indian student faces <b>nine steps including APS</b>, an American five with no embassy appointment, a French student three.",
    "Same German degree: an Indian passport on CBSE runs <b>20 steps including APS</b>. The same student on an IB diploma runs 17 &mdash; APS follows the board, not the passport. A US passport runs 15, a French one 11.",
    "objection: real per-student step counts")

sub("The <b>nine-step visa chain</b> above, with the steps that change by your student's nationality",
    "The <b>21-step application chain</b> above, filtered by passport, curriculum and country of residence",
    "what-you-get: 21-step chain, three axes")

sub("The visa route per nationality: who needs a Type D visa, who needs APS, who can skip the embassy.",
    "The route for the student in front of you: who needs a Type D visa, who can skip the embassy, and who needs APS &mdash; which follows the curriculum, not the passport.",
    "card 06: route per student, not per nationality")

sub("<strong>122 verified application and visa steps</strong>",
    "<strong>184 verified application and visa steps</strong>",
    "step total 122 -> 184")

# Tracks c and d collapse: the Type D route is one passport tier, and APS is
# a curriculum condition that cuts across it. Matched by regex - the source
# indentation is not stable enough for a literal.
NEW_TRACKS = """<div class="track c">
              <span class="badge">National (Type D) student visa</span>
              <h5>Every other passport</h5>
              <p class="who">All non-EU nationalities outside the eight above.</p>
              <p>The full Type D chain before travel. The variable that matters most is appointment availability at your student's local German mission, which swings from a fortnight to three months by country and season. Since 2026 the Consular Services Portal comes first and the VFS appointment link only appears at the end of a completed application, so booking early no longer works.</p>
            </div>
            <div class="track e">
              <span class="badge">Set by the curriculum, not the passport</span>
              <h5>APS and dMAT</h5>
              <p class="who">Any student holding a certificate issued by an Indian board &mdash; CBSE, ISC or a state board &mdash; wherever the school itself is.</p>
              <p>APS India is keyed on who issued the qualification, not on citizenship: <em>&ldquo;The applicant&rsquo;s nationality is not the decisive factor. What matters is whether the relevant academic documents were issued by Indian educational institutions.&rdquo;</em> So an Indian passport holder with an <b>IB or A-Level</b> diploma does not need APS, while a CBSE student does. Budget four weeks to three months. <strong>New for Summer Semester 2027:</strong> Indian Master's applicants from Engineering, Commerce, Accounting, Finance, Economics, Business or Management must also submit dMAT. <a href="https://aps-india.de/faqs/" target="_blank" rel="noopener">Source</a>.</p>
            </div>"""
import re as _re
_m = _re.search(r'<div class="track c">.*?</div>\s*<div class="track d">.*?</div>', s, _re.S)
if not _m: sys.exit("PATCH FAILED: track c/d block not found")
s = s[:_m.start()] + NEW_TRACKS + s[_m.end():]
print("  patched: tracks c/d -> passport tier c + curriculum-keyed APS card")

io.open(F, "w", encoding="utf-8").write(s)
print("\n%d -> %d bytes" % (len(orig), len(s)))
