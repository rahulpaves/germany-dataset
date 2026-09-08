#!/usr/bin/env python3
"""Prints the tagged links for each channel, plus what to look for in GoatCounter.

The page sanitises ?src to [A-Za-z0-9_-] and 24 characters, so every slug here
is chosen to survive that untouched. Whatever arrives in ?src is written into
the form's hidden "Came from" field, so a lead's channel is recorded without
anyone being asked where they came from.

    python3 campaign_links.py
    python3 campaign_links.py --check      # confirm each URL answers 200
"""
import sys, re, subprocess, urllib.parse

BASE = "https://germany.pavetheway.ai/"

CHANNELS = [
    ("linkedin",      "Organic LinkedIn posts"),
    ("linkedin-dm",   "One-to-one LinkedIn messages"),
    ("linkedin-ad",   "Paid LinkedIn, if you run any"),
    ("whatsapp",      "WhatsApp, one-to-one and groups"),
    ("email",         "Cold or warm email outreach"),
    ("referral",      "A counselor passing it to another"),
    ("newsletter",    "Any newsletter or community post"),
]

PITCH = ("47 English-taught German undergraduate degrees, with entry requirements "
         "per board, deadlines, fees and the visa steps for your student's passport. "
         "Free, and every field links to the university page it came from.")

def check(url):
    r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                        "--max-time", "20", "-L", url], capture_output=True, text=True)
    return r.stdout.strip()

verify = "--check" in sys.argv

print("\nCAMPAIGN LINKS\n" + "=" * 78)
for slug, what in CHANNELS:
    assert re.fullmatch(r"[A-Za-z0-9_-]{1,24}", slug), slug
    url = BASE + "?src=" + slug
    status = ("  [" + check(url) + "]") if verify else ""
    print("\n  %s%s" % (what, status))
    print("  %s" % url)
    print("  watch for: visit-%s  ->  hero-submit-%s / form-submit-%s  ->  CONVERSION-%s"
          % (slug, slug, slug, slug))

print("\n\nREADY-MADE WHATSAPP SHARE\n" + "=" * 78)
msg = PITCH + "\n\n" + BASE + "?src=whatsapp"
print("\n  https://wa.me/?text=" + urllib.parse.quote(msg))
print("\n  (opens WhatsApp with the message and the tagged link already written)")

print("\n\nSENDING THE FILE ITSELF\n" + "=" * 78)
print("""
  Campaign links above are for the landing page, where people sign up.
  Once somebody has signed up, send them their own file link instead:

      python3 make_link.py "Zara R" "CollegeLake"

  That one is per person, so you see who opened it and which programmes
  they read. Do not send file.html with a ?src tag; it is not a campaign
  link and you would lose the per-counselor tracking.
""")
