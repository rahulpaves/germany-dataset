# -*- coding: utf-8 -*-
"""Make the record's Entry requirements follow the chosen curriculum.

The list was hardcoded CBSE, ISC, IB, A-Level, US - so every counselor opened
on an Indian board regardless of the student in front of them. The board picker
now promotes the selected curriculum to the top and marks it.
"""
import io, os, sys
F = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "file.html")
s = io.open(F, encoding="utf-8").read(); orig = s
def sub(a, b, label, cnt=1):
    global s
    if a not in s: sys.exit("PATCH FAILED: " + label)
    s = s.replace(a, b, cnt); print("  patched:", label)

# req() gains an optional board id so the row can be found and moved later.
sub("function req(lead,val){return has(val)?'<li><b>'+esc(lead)+':</b> '+linky(val)+'</li>':'';}",
    "function req(lead,val,board){return has(val)?'<li'+(board?' data-board=\"'+board+'\"':'')+"
    "'><b>'+esc(lead)+':</b> '+linky(val)+'</li>':'';}",
    "req() carries a board id")

sub('        req("CBSE", r.cbse), req("ISC", r.isc), req("IB", r.ib), req("A-Level", r.alevel),\n'
    '        req("US High School Diploma", r.us_diploma_gpa),',
    '        req("CBSE", r.cbse, "cbse"), req("ISC", r.isc, "isc"), req("IB", r.ib, "ib"),\n'
    '        req("A-Level", r.alevel, "alevel"),\n'
    '        req("US High School Diploma", r.us_diploma_gpa, "us"),',
    "tag the five board rows")

# Persist the three choices across programme clicks.
sub("var CYCLES = null, CHAIN_HTML = \"\", CHAIN_TRACKS = null, ROUTES = null;",
    "var CYCLES = null, CHAIN_HTML = \"\", CHAIN_TRACKS = null, ROUTES = null;\n"
    "var SEL = {passport:null, board:null, residence:null};\n"
    "try{ var _s=JSON.parse(localStorage.getItem(\"paveSel\")||\"{}\");\n"
    "     if(_s && typeof _s===\"object\") SEL=_s; }catch(e){}\n"
    "function saveSel(){ try{ localStorage.setItem(\"paveSel\", JSON.stringify(SEL)); }catch(e){} }\n"
    "/* Move the chosen curriculum to the top of Entry requirements and mark it.\n"
    "   State boards read the CBSE row, which is what the data actually holds. */\n"
    "function orderReqs(board){\n"
    "  var ul=document.querySelector(\".reqs\"); if(!ul) return;\n"
    "  var want = board===\"state\" ? \"cbse\" : board;\n"
    "  var rows=ul.querySelectorAll(\"li[data-board]\");\n"
    "  for(var i=0;i<rows.length;i++) rows[i].classList.remove(\"picked\");\n"
    "  var hit=ul.querySelector('li[data-board=\"'+want+'\"]');\n"
    "  if(!hit) return;\n"
    "  hit.classList.add(\"picked\");\n"
    "  var first=ul.querySelector(\"li[data-board]\");\n"
    "  if(first && first!==hit) ul.insertBefore(hit, first);\n"
    "}",
    "SEL state + orderReqs()")

# buildNat: seed from SEL, write back on change, reorder the record rows.
sub('  selN.value = "India";\n  if(!selN.value) selN.value = names[0];',
    '  selN.value = SEL.passport || "India";\n  if(!selN.value) selN.value = names[0];',
    "seed passport from SEL")
sub('  selB.value = R.board.default || "cbse";',
    '  selB.value = SEL.board || R.board.default || "cbse";\n'
    '  if(!selB.value) selB.value = R.board.default || "cbse";',
    "seed curriculum from SEL")
sub('  selR.value = R.residence.default || "other";',
    '  selR.value = SEL.residence || R.residence.default || "other";\n'
    '  if(!selR.value) selR.value = R.residence.default || "other";',
    "seed residence from SEL")
sub("  function show(){\n    var country=selN.value, board=selB.value, res=selR.value;",
    "  function show(){\n    var country=selN.value, board=selB.value, res=selR.value;\n"
    "    SEL.passport=country; SEL.board=board; SEL.residence=res; saveSel();\n"
    "    orderReqs(board);",
    "persist + reorder on every change")

CSS = """
.reqs li.picked{background:#eef2ff;border-left:3px solid var(--primary);
  padding:7px 11px;margin-left:-14px;border-radius:0 6px 6px 0;}
.reqs li.picked b{color:#1b2f6e;}
</style>"""
sub("</style>", CSS, "picked-row CSS")
io.open(F, "w", encoding="utf-8").write(s)
print("\n%d -> %d bytes" % (len(orig), len(s)))
