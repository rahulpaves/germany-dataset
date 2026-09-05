#!/usr/bin/env python3
"""Build the per-counselor link for the Germany file.

    python3 make_link.py "Zara R" "CollegeLake"
    python3 make_link.py "Jehanne" "Zenith Education" --record DE-056

The slug in the link is what shows up in GoatCounter, so one person's opens are
always separable from everyone else's.
"""
import argparse, re, sys

BASE = "https://germany.pavetheway.ai/file.html"

def slug(*parts):
    s = " ".join(p for p in parts if p).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:40]

def first_token(name):
    """First name only, so the slug stays short and readable in the URL."""
    return name.split()[0] if name.split() else ""

ap = argparse.ArgumentParser()
ap.add_argument("name", help="counselor's name, e.g. \"Zara R\"")
ap.add_argument("org", nargs="?", default="", help="their agency or school")
ap.add_argument("--record", default="", help="open on one record, e.g. DE-056")
a = ap.parse_args()

token = slug(first_token(a.name), a.org)
if not token:
    sys.exit("need at least a name")

url = BASE + "?c=" + token + ("#" + a.record.upper() if a.record else "")

print()
print("  link      ", url)
print("  slug      ", token)
print("  watch for ", "file-open-" + token)
print()
print("  Add this line to NAMES in file.html so the page greets them properly:")
print('      "%s": "%s%s",' % (token, a.name, (", " + a.org) if a.org else ""))
print()
