#!/usr/bin/env python3
import re, sys, glob, os

def _resolve_vault():
    """Locate the Obsidian vault without hardcoding a per-session mount path.
    Order: $VAULT env var -> auto-detect a mounted dir containing @daily-notes
    -> the script's own ../../../.. (when run from vault/.claude/skills/.../scripts)."""
    import glob as _g
    cand = (os.environ.get("ovault") or os.environ.get("OVAULT")
            or os.environ.get("VAULT") or os.environ.get("OBSIDIAN_VAULT"))
    if cand and os.path.isdir(os.path.join(cand, "@daily-notes")):
        return os.path.abspath(cand)
    for base in _g.glob("/sessions/*/mnt/*") + _g.glob("/Users/*/Workspaces/*"):
        if os.path.isdir(os.path.join(base, "@daily-notes")):
            return os.path.abspath(base)
    here = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    if os.path.isdir(os.path.join(here, "@daily-notes")):
        return here
    raise SystemExit("daily-note-curator: could not locate the vault. "
                     "Set the VAULT environment variable to the vault root.")
VAULT = _resolve_vault()
DAILY = os.path.join(VAULT, "@daily-notes")

# --- Topic detection: (compiled regex over heading+body) -> topic note ---
# Patterns matched ONLY in the heading (generic words that reliably name the
# meeting subject in a title but are noise when they appear in body prose).
HEADING_ONLY = [
    (r"\bpricing\b|\bquote\b|\bquoting\b|\binvoic", "Proceed"),
    # "AI adoption" is an ongoing initiative everyone name-drops in 1:1s, so it is
    # noise in body text. Only tag the project when the meeting is titled about it.
    (r"AI adoption", "AI adoption bench project"),
    # NOTE: review meetings are NOT auto-linked to a generic hub. The 2026 review cycle is
    # split into distinct project hubs (2026 Reviews - Self / 360 Peer / Phase 1 (CTI) /
    # Manager). A review-titled meeting should link the SPECIFIC project it belongs to,
    # which is a judgment call -- surface it and link by hand rather than guessing.
]

TOPIC_RULES = [
    (r"\bproceed\b|\bAI TOC\b|table of contents|\bDEX\b|council press|counselpress", "Proceed"),
    (r"\bocta|data harmony|\bOUSA\b|\bokta\b|aquafarma|octifarmer|octopharma|octa pharma", "Octapharma"),
    (r"\bdoordash\b|\bDD\b", "DoorDash"),
    (r"\bBSC\b", "BSC"),
    (r"\bverizon\b", "Verizon"),
    (r"\bHBP\b|\bHPP\b|\bHVP\b|harvard", "HBP"),
    (r"\bTJX\b", "TJX"),
    (r"\bralliant\b", "Ralliant"),
    (r"philadelphia eagles|\beagles\b", "Philadelphia Eagles"),
    (r"NF North America|\bNF NA\b", "NF North America"),
    (r"horizon tax", "Horizon Tax"),
    (r"\bATG\b|alliance technical group", "ATG"),
    (r"priority power", "Priority Power"),
    (r"powerplan|power plan", "Powerplan"),
    (r"\bscout\b", "Scout Clinical"),
    (r"\bclover\b", "Clover"),
    (r"\bGATX\b", "GATX"),
    (r"\bnabors\b", "Nabors"),
    (r"\blabtician\b", "Labtician"),
    (r"\bSMPA\b|\bSNPA\b", "SMPA"),
    (r"care hospice", "Care Hospice"),
    (r"point 32|point32|\bP32\b", "Point 32"),
    (r"\bCVS\b", "CVS"),
    (r"teradyne|teradine", "Teradyne"),
    (r"new leaders", "New Leaders"),
    (r"new york life|\bNYL\b", "New York Life"),
    (r"\bdynapar\b|\bdinapar\b|dinopar|dyna.?mpar|dyna par|dina par", "Dynapar"),
    (r"tokyo century|tokyo sentry", "Tokyo Century"),
    (r"\bstellix\b|\bstelix\b|\bstellex\b|\bstelex\b|installix", "Stellix"),
    (r"brookwood", "Brookwood"),
    (r"\bNOV\b", "NOV"),
    (r"\bUC7\b", "AI adoption bench project"),
    (r"core moto", "Core Moto"),
    # curated themes
    (r"staffing|recruit|staff demand|\bRIF\b|role description|layoff", "Staffing and allocation"),
    (r"data governance|\bDG\b", "Data governance"),
]
COMPILED = [(re.compile(p, re.I), t) for p, t in TOPIC_RULES]
COMPILED_HEAD = [(re.compile(p, re.I), t) for p, t in HEADING_ONLY]

THEMES = {"Staffing and allocation", "AI adoption bench project", "Data governance"}
# Per the 2026-06 rule update, recurring roster/status meetings (Staffing Weekly, Pipeline
# Review, All Hands, Leadership Team, Practice Directors) DO get per-client topic links for
# every client discussed in body, in addition to the theme. The old "theme-only" filter is
# removed; clients now flow through the normal detection path.

# --- People: search-string -> canonical note (longest first) ---
# Aliases: note-taker spellings / short forms -> the canonical hub filename.
# Canonical full names are auto-discovered from the people/ folders (below), so only
# non-identity mappings live here. Bare "Hari" is intentionally absent (ambiguous:
# Harikrishna Sorakayala vs the client-side "Hari Kaddar" on Ralliant) -- link by hand.
ALIASES = {
    "Venkat": "Venkata Vakalapudi",
    "Matthew Richie": "Matthew Ritchie", "Matt Richie": "Matthew Ritchie",
    "Anil Bhardawa": "Anil Bharadwa",
    "Nagrendra Ponna": "Nagendra Ponna",
    "Naveen Ballusupalli": "Naveen Babu Balusupalli",
    "Jeff St Germain": "Jeff St Germaine",
    "Viswanth Thatha": "Viswanath Thatha",
    "Ankitha Thiralka": "Ankitha Thirakala",
    "harikris2105": "Harikrishna Sorakayala",
    "Kaddar Subba Maniyani": "Hari Kaddar",
    # 2026-06 additions
    "Lamya Tawfik": "Lamya Tawfic",
    "Vishwa": "Viswanath Thatha",
    "Santos": "Santosh Badhri",
    "Santhosh Badhri": "Santosh Badhri",
    "Malik": "Malik Khan",
    "Mason": "Mason Reiter",
    "Pete Peralta": "Peter Peralta",
    # 2026-07 additions (this run)
    "Nick Pompa": "Nicholas Pompa",
    "Surya Kumar Ayala Somayajula": "Surya", "Surya Kumar": "Surya",
    "Lamia": "Lamya Tawfic",
    "Sky Woo": "Sky Wu",
    "Dustin Gabral": "Dustin Cabral",
    "Barbara Lunzi": "Barbara Lindsey",
    "Sedir": "Sudheer Siddhineni",
}

# Hub filenames that EXIST (so they can be hand-linked) but must NOT be auto-wrapped by the
# attendee linker, because the bare token is a common/ambiguous first name that would
# false-match unrelated people. Prefer renaming a hub to a full name over adding it here;
# use this only when a full name can't be obtained (fallback guard).
EXCLUDE_AUTOLINK = {"Babak", "Bonny", "Chettle"}

def build_people():
    """Discover canonical person names from every people/ hub folder, then layer aliases."""
    import glob as _g
    m = {}
    roots = ([os.path.join(VAULT, "cleartelligence", "people")] +
             _g.glob(os.path.join(VAULT, "cleartelligence", "clients", "*", "people")) +
             _g.glob(os.path.join(VAULT, "cleartelligence", "partners", "*", "people")))
    for d in roots:
        if not os.path.isdir(d): continue
        for f in os.listdir(d):
            if f.endswith(".md"):
                nm = f[:-3]; m[nm] = nm
    m.update(ALIASES)
    for x in EXCLUDE_AUTOLINK:
        m.pop(x, None)
    return m

PEOPLE = build_people()
SEARCH_ORDER = sorted(PEOPLE.keys(), key=len, reverse=True)

def detect_topics(heading, body):
    text = heading + "\n" + body
    found = []
    for rx, topic in COMPILED:
        if rx.search(text) and topic not in found:
            found.append(topic)
    for rx, topic in COMPILED_HEAD:
        if rx.search(heading) and topic not in found:
            found.append(topic)
    return found

def link_attendees(line):
    out = line
    for s in SEARCH_ORDER:
        canon = PEOPLE[s]
        # replace whole-word s not already inside [[...]]
        pat = re.compile(r"(?<!\[\[)\b" + re.escape(s) + r"\b(?!\]\])")
        out = pat.sub("[[" + canon + "]]", out)
    # collapse accidental nested like [[X]] from alias then canonical (canon==s handled by guard)
    return out

def process(path, apply=False, add=None):
    with open(path) as f:
        lines = f.read().split("\n")
    # find meeting section boundaries (## headings, not ### )
    idx = [i for i,l in enumerate(lines) if re.match(r"^## ", l)]
    sections = []
    for k,i in enumerate(idx):
        end = idx[k+1] if k+1 < len(idx) else len(lines)
        sections.append((i,end))
    report = []
    # process from bottom up so insertion indices stay valid
    for (i,end) in reversed(sections):
        heading = lines[i]
        body = "\n".join(lines[i+1:end])
        topics = detect_topics(heading, body)
        # find attendee line: first non-empty line after heading that's not ###, not -, not **Topics
        att_rel = None
        for j in range(i+1, end):
            s = lines[j].strip()
            # skip blank lines and existing Topics/Tags metadata so re-runs find attendees
            if s == "" or s.startswith("**Topics:") or s.startswith("**Tags:"): continue
            if s.startswith("#") or s.startswith("-"):
                break
            att_rel = j; break
        # link attendees
        if att_rel is not None:
            newl = link_attendees(lines[att_rel])
            if newl != lines[att_rel] and apply:
                lines[att_rel] = newl
        if add:
            # TARGETED backfill of one newly-created hub: add [[add]] only where the hub's
            # name literally appears (word-boundary), appending to an existing Topics line or
            # inserting one. Safe and idempotent, the topic analog of wrapping a new person's
            # name. Full re-detection of all topics is deliberately NOT done here, because
            # that would re-add hand-removed topics and surface keyword false positives.
            if re.search(r'(?<!\[)\b' + re.escape(add) + r'\b(?!\])', heading + "\n" + body, re.I):
                tline = None
                for j in range(i+1, min(i+6, end)):
                    if lines[j].strip().startswith("**Topics:"):
                        tline = j; break
                if tline is not None:
                    items = re.findall(r"\[\[([^\]]+)\]\]", lines[tline])
                    if add not in items and apply:
                        lines[tline] = "**Topics:** " + ", ".join("[[%s]]" % t for t in items + [add])
                elif apply:
                    ins = i + 1
                    if ins < len(lines) and lines[ins].strip() == "":
                        ins += 1
                    lines.insert(ins, "")
                    lines.insert(ins, "**Topics:** [[%s]]" % add)
        else:
            # Default run: insert a Topics line only when the section has none yet. Re-running
            # full topic detection over an already-curated section is NOT safe (heuristic
            # rules have false positives and Jason curates topics by hand), so we never
            # re-detect into existing Topics lines. Use --add to backfill a new hub.
            already = any(lines[j].strip().startswith("**Topics:") for j in range(i+1, min(i+5,end)))
            if topics and not already and apply:
                ins = i + 1
                if ins < len(lines) and lines[ins].strip() == "":
                    ins += 1
                lines.insert(ins, "")
                lines.insert(ins, "**Topics:** " + ", ".join("[[%s]]" % t for t in topics))
        report.append((heading.strip(), topics))
    if apply:
        with open(path,"w") as f:
            f.write("\n".join(lines))
    return list(reversed(report))

if __name__ == "__main__":
    apply = "--apply" in sys.argv
    # --add "Hub Name": targeted backfill of one newly-created hub (adds [[Hub]] where its
    # name literally appears), instead of the default topic-detection pass.
    add = None
    if "--add" in sys.argv:
        ai = sys.argv.index("--add")
        if ai + 1 < len(sys.argv): add = sys.argv[ai + 1]
    # First non-flag arg is a glob pattern (default: all of the 2026 folder).
    pat = next((a for a in sys.argv[1:] if not a.startswith("-") and a != add), "2026/*.md")
    files = sorted(glob.glob(os.path.join(DAILY, pat)))
    for fp in files:
        rep = process(fp, apply=apply, add=add)
        rep = [r for r in rep if r[1] or True]
        if not rep: continue
        print("\n### " + os.path.basename(fp))
        for h,t in rep:
            print(f"  {h}\n      -> Topics: {', '.join(t) if t else '(none)'}")
    print("\nMODE:", "APPLIED" if apply else "DRY RUN")
