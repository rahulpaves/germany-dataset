# -*- coding: utf-8 -*-
"""Replace the single nationality picker with three axis pickers.

file.html is a headless fragment - there is no </head>, so CSS goes after the
first </style>. Every replacement asserts it actually fired; a silent no-op is
the failure mode that has bitten this file before.
"""
import io, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
F = os.path.join(os.path.dirname(HERE), "file.html")
s = io.open(F, encoding="utf-8").read()
orig = s
n = [0]

def sub(old, new, label, count=1):
    global s
    if old not in s:
        sys.exit("PATCH FAILED - anchor not found: " + label)
    s = s.replace(old, new, count)
    n[0] += 1
    print("  patched:", label)

# ---------------------------------------------------------------- 1. CSS ----
CSS = """
/* three-axis route picker: passport / curriculum / applying-from */
.natpick{display:block;}
.axrow{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;}
@media(max-width:720px){.axrow{grid-template-columns:1fr;}}
.axf label{display:block;font-size:12.5px;font-weight:600;color:var(--ink);margin-bottom:6px;}
.axf select{width:100%;max-width:none;}
.axnote{margin:10px 0 0;padding:10px 13px;font-size:13.5px;line-height:1.55;
  border-radius:8px;background:#eef2ff;border:1px solid #c9d4ff;color:#1f2a44;}
.axnote b{color:#1b2f6e;}
.axnote.warn{background:#fff8e6;border-color:#f0d99b;color:#4a3c10;}
.axnote.warn b{color:#7a5c00;}
.axwhy{margin:9px 0 0;font-size:12.5px;line-height:1.5;opacity:.8;}
.axwhy a{color:#2b4fe3;}
</style>"""
sub("</style>", CSS, "route-picker CSS (after first </style>)")

# ------------------------------------------------------------- 2. markup ----
sub(
 '\'<div class="natpick"><label for="nat">Check your student\\\'s nationality</label>\'+\n'
 '      \'<select id="nat"><option value="">Show the standard non-EU route</option></select></div>\'+',
 '\'<div class="natpick"><div class="axrow">\'+\n'
 '        \'<div class="axf"><label for="nat">Passport</label><select id="nat"></select></div>\'+\n'
 '        \'<div class="axf"><label for="brd">Curriculum</label><select id="brd"></select></div>\'+\n'
 '        \'<div class="axf"><label for="res">Applying from</label><select id="res"></select></div>\'+\n'
 '      \'</div></div>\'+',
 "picker markup (one select -> three)")

# ------------------------------------------------- 3. emit axes on steps ----
sub("""  var li = steps.map(function(st){
    var who = String(st.who || "").toLowerCase().split(/[\\s,]+/).filter(Boolean).join(" ");
    var dur""",
"""  var li = steps.map(function(st){
    var ax = st.axes || {};
    var A = function(k){ return (ax[k] || []).join(" "); };
    var dur""",
 "buildTimeline: read axes instead of who")

sub("""      ' data-tracks="' + esc(who) + '" data-stage="' + esc(st.stage || "") + '">' +""",
"""      ' data-passport="' + esc(A("passport")) + '"' +
      ' data-board="' + esc(A("board")) + '"' +
      ' data-residence="' + esc(A("residence")) + '"' +
      ' data-stage="' + esc(st.stage || "") + '">' +""",
 "buildTimeline: emit three data attributes")

sub("""  var toks = {};
  steps.forEach(function(st){
    String(st.who || "").split(/[\\s,]+/).filter(Boolean).forEach(function(t){ toks[t.toLowerCase()] = 1; });
  });
  CHAIN_TRACKS = Object.keys(toks);""",
"""  CHAIN_TRACKS = null;""",
 "buildTimeline: drop the old track sniffing")

# --------------------------------------------------- 4. replace buildNat ----
start = s.index("function buildNat(){")
end = s.index("function list(){")
NEW = r'''function buildNat(){
  var selN=document.getElementById("nat"), selB=document.getElementById("brd"),
      selR=document.getElementById("res"), out=document.getElementById("natout");
  if(!selN || !ROUTES || !ROUTES[COUNTRY]) return;
  var R = ROUTES[COUNTRY], TIERS = R.passport.tiers;

  /* passport -> tier. Countries are listed under exactly one tier. */
  var TIER_OF = {};
  TIERS.forEach(function(t){ (t.countries||[]).forEach(function(c){ TIER_OF[c]=t.id; }); });
  function tierObj(id){
    for(var i=0;i<TIERS.length;i++) if(TIERS[i].id===id) return TIERS[i];
    return null;
  }
  var names = Object.keys(TIER_OF).sort();
  selN.innerHTML = names.map(function(c){
    return '<option value="'+esc(c)+'">'+esc(c)+'</option>';
  }).join("");
  selN.value = "India";
  if(!selN.value) selN.value = names[0];

  selB.innerHTML = (R.boards||[]).map(function(b){
    return '<option value="'+esc(b.id)+'">'+esc(b.name)+'</option>';
  }).join("");
  selB.value = R.board.default || "cbse";

  selR.innerHTML = (R.residence.options||[]).map(function(o){
    return '<option value="'+esc(o.id)+'">'+esc(o.name)+'</option>';
  }).join("");
  selR.value = R.residence.default || "other";

  function resObj(id){
    var o = R.residence.options||[];
    for(var i=0;i<o.length;i++) if(o[i].id===id) return o[i];
    return null;
  }

  /* A step shows unless an axis names a set it is not in. Empty = everyone. */
  function applyAxes(tier, board, res){
    var li=document.querySelectorAll(".timeline li[data-stage]"), n=0, seen={};
    function ok(el, attr, val){
      var raw=(el.getAttribute(attr)||"").trim();
      if(!raw) return true;
      return raw.split(/\s+/).indexOf(val) > -1;
    }
    for(var i=0;i<li.length;i++){
      var e=li[i];
      var on = ok(e,"data-passport",tier) && ok(e,"data-board",board) && ok(e,"data-residence",res);
      e.hidden = !on;
      e.classList.remove("stage-start");
      if(on){
        n++;
        var b=e.querySelector(".n"); if(b) b.textContent=n;
        var st=e.getAttribute("data-stage");
        if(!seen[st]){ seen[st]=1; e.classList.add("stage-start"); e.setAttribute("data-stagelabel",st); }
      }
    }
    return n;
  }

  function show(){
    var country=selN.value, board=selB.value, res=selR.value;
    var tid = TIER_OF[country] || R.passport.default;
    var t = tierObj(tid), r = resObj(res);
    var total = document.querySelectorAll(".timeline li[data-stage]").length;
    var n = applyAxes(tid, board, res);
    var bn = (R.board.notes||{})[board] || "";
    var bname = "";
    (R.boards||[]).forEach(function(b){ if(b.id===board) bname=b.name; });

    var html = '<b>'+esc(country)+' passport &middot; '+esc(bname)+
      (r && r.id!=="other" ? ' &middot; applying from '+esc(r.name) : '')+'</b>'+
      '<div style="margin-top:8px;font-size:13.5px;opacity:.9">'+
        esc(t ? t.name : "")+' &mdash; '+esc(t ? t.summary : "")+
      '</div>'+
      '<div style="margin-top:8px;font-size:13.5px;"><b>'+n+' of '+total+
        ' steps</b> apply to this student.</div>';
    if(bn) html += '<p class="axnote"><b>'+esc(bname)+':</b> '+bn+'</p>';
    if(r && r.note) html += '<p class="axnote warn"><b>'+esc(r.name)+':</b> '+r.note+'</p>';
    var src = (t && t.source_url) || (r && r.source_url) || "";
    if(src) html += '<p class="axwhy">Route rule: <a href="'+esc(src)+
      '" target="_blank" rel="noopener">official source</a>'+
      (R.date_checked ? ' &middot; checked '+esc(R.date_checked) : '')+'</p>';
    out.innerHTML = html;
    out.classList.add("on");
  }
  selN.addEventListener("change",show);
  selB.addEventListener("change",show);
  selR.addEventListener("change",show);
  show();
}

'''
s = s[:start] + NEW + s[end:]
n[0] += 1
print("  patched: buildNat -> three-axis buildNat")

# --------------------------------------------- 5. load routes.json + drop ----
sub("var CYCLES = null, CHAIN_HTML = \"\", CHAIN_TRACKS = null;",
    "var CYCLES = null, CHAIN_HTML = \"\", CHAIN_TRACKS = null, ROUTES = null;",
    "declare ROUTES")

# Germany's hardcoded fallback chain predates the axes and would never filter.
sub('(CHAIN_HTML || (COUNTRY === "germany" ? TIMELINE_HTML : ""))',
    'CHAIN_HTML',
    "drop the pre-axes hardcoded Germany timeline fallback")

io.open(F, "w", encoding="utf-8").write(s)
print("\n%d edits applied, %d -> %d bytes" % (n[0], len(orig), len(s)))
