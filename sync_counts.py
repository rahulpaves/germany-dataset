#!/usr/bin/env python3
"""
Recompute the CONFIG counts in index.html from data.json.

The counts on the page were hand-maintained and drifted from the data they
describe. On a page whose entire pitch is "we don't publish what we haven't
checked", a wrong count is the most expensive kind of bug: it is the one a
sceptical counsellor can catch in ten seconds.

Everything here counts DISTINCT (country, institution, programme) triples, so
duplicate rows in data.json can never inflate a public number.

    python3 sync_counts.py            # report drift, change nothing
    python3 sync_counts.py --apply    # rewrite the CONFIG block in index.html
"""
import json, re, sys, pathlib

HERE = pathlib.Path(__file__).parent
DATA = HERE / "data.json"
PAGE = HERE / "index.html"


def key(r):
    return (r.get("country"), r.get("institution"), r.get("programme"))


def is_note(r):
    """Some rows carry an annotation in the programme field rather than a
    programme, e.g. 'NOTE: All BAs require C1 German'. They record a real
    finding (this university has no English bachelor's) and are worth keeping,
    but they are not programmes and must never be counted as one."""
    return str(r.get("programme", "")).startswith("NOTE:")


def counts():
    rows = json.loads(DATA.read_text())
    uniq = {key(r): r for r in rows if not is_note(r)}    # last wins; exact dupes collapse
    notes = {key(r): r for r in rows if is_note(r)}
    verified = {k for k, r in uniq.items() if r.get("verified")}

    per_country = {}
    for (country, inst, _prog) in uniq:
        p, i = per_country.setdefault(country, [0, set()])
        per_country[country][0] = p + 1
        i.add(inst)

    de = [k for k in uniq if k[0] == "Germany"]
    de_verified = [k for k in de if k in verified]
    return {
        "rows_in_file":     len(rows),
        "NOTE_ROWS":        len(notes),
        "PROGRAMME_COUNT":  len(de),
        "GERMANY_VERIFIED": len(de_verified),
        "UNI_COUNT":        len({i for (_c, i, _p) in de}),
        "TOTAL_PROGRAMMES": len(uniq),
        "TOTAL_INSTS":      len({i for (_c, i, _p) in uniq}),
        "TOTAL_COUNTRIES":  len({c for (c, _i, _p) in uniq}),
        "VERIFIED_PROGRAMMES": len(verified),
        "COUNTRY_DATA": {c: [n, len(insts)] for c, (n, insts) in per_country.items()},
    }


def current(page):
    out = {}
    for name in ("TOTAL_PROGRAMMES", "TOTAL_INSTS", "TOTAL_COUNTRIES",
                 "VERIFIED_PROGRAMMES", "UNI_COUNT", "PROGRAMME_COUNT",
                 "GERMANY_VERIFIED"):
        m = re.search(r"^\s*%s:\s*(\d+)," % name, page, re.M)
        out[name] = int(m.group(1)) if m else None
    return out


def main():
    apply = "--apply" in sys.argv
    page = PAGE.read_text()
    c, have = counts(), current(PAGE.read_text())

    dupes = c["rows_in_file"] - c["TOTAL_PROGRAMMES"] - c["NOTE_ROWS"]
    print("data.json: %d rows, %d distinct programmes "
          "(%d duplicate row%s, %d annotation row%s excluded)"
          % (c["rows_in_file"], c["TOTAL_PROGRAMMES"], dupes, "" if dupes == 1 else "s",
             c["NOTE_ROWS"], "" if c["NOTE_ROWS"] == 1 else "s"))

    drift = False
    for name in ("UNI_COUNT", "PROGRAMME_COUNT", "GERMANY_VERIFIED", "TOTAL_PROGRAMMES",
                 "TOTAL_INSTS", "TOTAL_COUNTRIES", "VERIFIED_PROGRAMMES"):
        truth, shown = c[name], have[name]
        if shown != truth:
            drift = True
            print("  DRIFT  %-20s page says %-6s data says %s" % (name, shown, truth))
        else:
            print("  ok     %-20s %s" % (name, truth))

    # per-country picker numbers
    m = re.search(r"COUNTRY_DATA:\s*\{(.*?)\n  \},", page, re.S)
    if m:
        shown = {c: (int(a), int(b)) for c, a, b in
                 re.findall(r'"([^"]+)":\[(\d+),(\d+)\]', m.group(1))}
        for country, (n, insts) in sorted(c["COUNTRY_DATA"].items()):
            s = shown.get(country)
            if not s:
                drift = True
                print("  DRIFT  COUNTRY_DATA missing %s (data says %d/%d)" % (country, n, insts))
            elif s != (n, insts):
                drift = True
                print("  DRIFT  COUNTRY_DATA %-14s page says %s/%s  data says %d/%d"
                      % (country, s[0], s[1], n, insts))

    if not drift:
        print("\nNo drift. Page matches data.")
        return

    if not apply:
        print("\nRun with --apply to rewrite index.html.")
        return

    for name in ("TOTAL_PROGRAMMES", "TOTAL_INSTS", "TOTAL_COUNTRIES",
                 "UNI_COUNT", "PROGRAMME_COUNT", "GERMANY_VERIFIED"):
        page = re.sub(r"^(\s*%s:\s*)\d+," % name, r"\g<1>%d," % c[name], page, count=1, flags=re.M)

    if have["GERMANY_VERIFIED"] is None:
        page = re.sub(r"^(\s*PROGRAMME_COUNT:\s*\d+,)",
                      r"\1\n  GERMANY_VERIFIED: %d," % c["GERMANY_VERIFIED"],
                      page, count=1, flags=re.M)

    if have["VERIFIED_PROGRAMMES"] is None:
        page = re.sub(r"^(\s*TOTAL_PROGRAMMES:\s*\d+,)",
                      r"\1\n  VERIFIED_PROGRAMMES: %d," % c["VERIFIED_PROGRAMMES"],
                      page, count=1, flags=re.M)
    else:
        page = re.sub(r"^(\s*VERIFIED_PROGRAMMES:\s*)\d+,",
                      r"\g<1>%d," % c["VERIFIED_PROGRAMMES"], page, count=1, flags=re.M)

    body = "\n".join(
        "    " + " ".join('"%s":[%d,%d],' % (co, n, i) for co, (n, i) in chunk)
        for chunk in [sorted(c["COUNTRY_DATA"].items(), key=lambda kv: -kv[1][0])[i:i + 4]
                      for i in range(0, len(c["COUNTRY_DATA"]), 4)]
    ).rstrip(",")
    page = re.sub(r"(COUNTRY_DATA:\s*\{).*?(\n  \},)", r"\1\n" + body.replace("\\", "\\\\") + r"\2",
                  page, count=1, flags=re.S)

    PAGE.write_text(page)
    print("\nindex.html updated.")


if __name__ == "__main__":
    main()
