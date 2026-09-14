# -*- coding: utf-8 -*-
import io, os, sys, re
F = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "file.html")
s = io.open(F, encoding="utf-8").read(); orig=s

def sub(a,b,label):
    global s
    if a not in s: sys.exit("PATCH FAILED: "+label)
    s = s.replace(a,b,1); print("  patched:", label)

sub('fetch("data/cycles.json?v=" + V).then(function(r){ return r.json(); })\n'
    '  .then(function(cy){ CYCLES = cy; }).catch(function(){})\n',
    'fetch("data/cycles.json?v=" + V).then(function(r){ return r.json(); })\n'
    '  .then(function(cy){ CYCLES = cy; }).catch(function(){})\n'
    '  .then(function(){ return fetch("data/routes.json?v=" + V); })\n'
    '  .then(function(r){ return r.json(); })\n'
    '  .then(function(rt){ ROUTES = rt; }).catch(function(){})\n',
    "fetch routes.json")

# Strip the three dead Germany-only globals the axes model replaces.
for name in ("TRACKS", "TRACK_SUMMARY", "COUNTRY_NOTES", "TIMELINE_HTML"):
    m = re.search(r'^(?:const|var) '+name+r'\s*=.*?;\s*$', s, re.M|re.S)
    if not m: sys.exit("could not locate "+name)
    s = s[:m.start()] + s[m.end():]
    print("  removed dead global:", name, "(%d bytes)" % (m.end()-m.start()))

io.open(F,"w",encoding="utf-8").write(s)
print("\n%d -> %d bytes" % (len(orig), len(s)))
