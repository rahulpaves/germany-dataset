#!/usr/bin/env python3
"""Regenerates share.png, the picture LinkedIn and WhatsApp show for a link.

The previous one was rendered once from HTML that was never saved, so when the
count changed from 58 to 47 the meta title updated and the picture kept saying
58. Numbers here come from germany-file.json, so running this after a data
change is all it takes.

    python3 make_share_image.py
"""
import json, subprocess, pathlib, sys

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

d = json.load(open("germany-file.json"))
META = {"record_id","verified_status","corrected_value_if_any","source_url_you_used",
        "exact_quote","date_checked","link_works","checked_by","deadline_iso"}
keys = {k for r in d for k in r if k not in META}
fills = sorted(sum(1 for k in keys if str(r.get(k) or "").strip()) for r in d)
n     = len(d)
unis  = len({r["institution"] for r in d})
floor = fills[0]
typical = max(set(fills), key=fills.count)

html = """<!DOCTYPE html><html><head><meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap">
<style>
  *{margin:0;padding:0;box-sizing:border-box;}
  body{width:1200px;height:630px;font-family:Inter,-apple-system,sans-serif;
       background:#fff;color:#0d1b2a;position:relative;overflow:hidden;}
  .bg{position:absolute;inset:0;background:
      radial-gradient(900px 460px at 88%% -12%%, #e8eeff 0%%, rgba(255,255,255,0) 62%%);}
  .wrap{position:relative;padding:66px 74px;height:100%%;display:flex;flex-direction:column;}
  .chip{display:inline-flex;align-items:center;gap:9px;align-self:flex-start;
        font-size:17px;font-weight:600;color:#3d5570;background:#fff;
        border:1px solid #dfe6ef;border-radius:999px;padding:9px 18px;margin-bottom:38px;}
  h1{font-size:64px;line-height:1.08;font-weight:800;letter-spacing:-1.6px;max-width:1010px;}
  h1 span{color:#2b4fe3;}
  p.sub{font-size:25px;line-height:1.46;color:#41556b;margin-top:26px;max-width:930px;}
  p.sub b{color:#0d1b2a;font-weight:700;}
  .foot{margin-top:auto;display:flex;align-items:center;gap:16px;
        font-size:19px;color:#41556b;font-weight:500;}
  .dot{width:7px;height:7px;border-radius:50%%;background:#2b4fe3;}
  .brand{font-size:22px;font-weight:800;color:#2b4fe3;letter-spacing:-.4px;margin-left:auto;}
</style></head><body>
<div class="bg"></div>
<div class="wrap">
  <div class="chip">&#127465;&#127466; For counselors &middot; Germany</div>
  <h1>%(n)d English-taught German undergraduate degrees. <span>Every answer, in one file.</span></h1>
  <p class="sub">Entry requirements per board, deadlines, fees, and the visa steps that change
     with your student's passport. <b>%(floor)d fields on every programme, %(typical)d on most</b>,
     each one checked against the university's own page.</p>
  <div class="foot"><span class="dot"></span> %(n)d programmes across %(unis)d German institutions
     &middot; every source link live<span class="brand">germany.pavetheway.ai</span></div>
</div></body></html>""" % dict(n=n, unis=unis, floor=floor, typical=typical)

src = pathlib.Path("share-source.html"); src.write_text(html)
out = pathlib.Path("share.png").resolve()
r = subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
                    "--force-device-scale-factor=2", "--window-size=1200,630",
                    "--virtual-time-budget=6000",
                    "--screenshot=" + str(out), str(src.resolve())],
                   capture_output=True, text=True)
if not out.exists():
    sys.exit("render failed: " + r.stderr[-500:])
subprocess.run(["sips", "-z", "630", "1200", str(out)], capture_output=True)
size = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(out)],
                      capture_output=True, text=True).stdout
print("share.png rebuilt: %d programmes, %d institutions, %d/%d fields" % (n, unis, floor, typical))
print(size.strip())
