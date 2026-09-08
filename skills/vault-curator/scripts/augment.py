#!/usr/bin/env python3
"""Augment daily notes: append project-hub topics to existing Topics lines, and add a
meeting-type **Tags:** line. Additive and idempotent (never removes existing topics)."""
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
VAULT=_resolve_vault()
DAILY=os.path.join(VAULT,"@daily-notes")
CLIENTS={d.lower() for d in os.listdir(os.path.join(VAULT,"cleartelligence","clients"))
         if os.path.isdir(os.path.join(VAULT,"cleartelligence","clients",d))}
# client-side people = anyone with a hub under a client's people/ folder. A meeting is a
# client meeting only if one of THEM attended, not merely if a client is a topic.
CLIENT_PEOPLE={os.path.splitext(f)[0] for d in glob.glob(os.path.join(VAULT,"cleartelligence","clients","*","people")) for f in os.listdir(d) if f.endswith(".md")}

# project topic -> (regex, heading_only)
PROJECTS=[
    ("Pricing", re.compile(r"\bpricing\b|\bquote\b|\bquoting\b|\binvoic", re.I), True),
    ("DEX", re.compile(r"\bDEX\b|AI TOC|table of contents|\bdecks\b", re.I), False),
    ("Data Harmony", re.compile(r"data harmony", re.I), False),
    ("AI Regulatory Reporting", re.compile(r"regulatory reporting|forbearance|ILEC", re.I), False),
    ("Verizon Finance AI Strategy", re.compile(r"finance ai strategy|finance ai council", re.I), False),
]
INTERNAL_TYPES=[
    ("#interview", re.compile(r"\binterview\b|confirmation of .*interview|candidate", re.I)),
    ("#all-hands", re.compile(r"all[- ]hands", re.I)),
    ("#1on1", re.compile(r"\b1:1\b|1 on 1|/ ?jason|jason ?/|jason and |and jason", re.I)),
    ("#leadership", re.compile(r"leadership team|practice directors|leads meeting|leads connect", re.I)),
    ("#recruiting", re.compile(r"recruit|role description|role alignment|role sync|\bhiring\b", re.I)),
    ("#team-sync", re.compile(r"team leads|bi-?weekly|sync-?up|tag ?up|check-?in|regroup|\bconnect\b|\bsync\b|staffing weekly", re.I)),
]

def topic_items(line):
    body=line.split("**Topics:**",1)[1] if "**Topics:**" in line else ""
    return [t.strip() for t in body.split(",") if t.strip()]

_link=re.compile(r'\[\[([^\]|#]+)')
def attendee_names(L, i, end):
    """Names on the section's attendee line (first non-empty, non-meta, non-bullet line)."""
    for j in range(i+1, end):
        s=L[j].strip()
        if s=="" or s.startswith("**Topics:") or s.startswith("**Tags:"): continue
        if s.startswith("#") or s.startswith("-"): return set()
        names=set(_link.findall(s))
        names |= {t.strip() for t in re.sub(r'\[\[|\]\]','',s).split(",")}
        return names
    return set()

def tags_for(heading, client_attendee):
    primary=None
    for tag,rx in INTERNAL_TYPES:
        if rx.search(heading): primary=tag; break
    # Context tag is based on WHO attended: a client-side person present = client meeting,
    # otherwise an internal meeting (even when the subject is a client, e.g. a KT or prep).
    tags=([primary] if primary else []) + ["#client-meeting" if client_attendee else "#internal-meeting"]
    out=[]
    for t in tags:
        if t not in out: out.append(t)
    return out

def process(path, apply=False):
    L=open(path).read().split("\n")
    idx=[i for i,l in enumerate(L) if l.startswith("## ")]
    changes=[]
    # work bottom-up
    for k in range(len(idx)-1,-1,-1):
        i=idx[k]; end=idx[k+1] if k+1<len(idx) else len(L)
        heading=L[i][3:].strip()
        # locate topics line + tags line within section
        tline=None; tagline=None
        for j in range(i+1,end):
            if L[j].startswith("**Topics:**"): tline=j
            if L[j].startswith("**Tags:**"): tagline=j
        body="\n".join(L[i+1:end])
        # --- project augmentation ---
        if tline is not None:
            items=topic_items(L[tline])
            present={re.sub(r'\[\[|\]\]','',x).lower() for x in items}
            for proj,rx,honly in PROJECTS:
                hay=heading if honly else heading+"\n"+body
                if rx.search(hay) and proj.lower() not in present:
                    items.append(f"[[{proj}]]"); present.add(proj.lower())
            newtopics="**Topics:** "+", ".join(items)
            if newtopics!=L[tline]:
                if apply: L[tline]=newtopics
                changes.append(("topics",heading,newtopics))
        # --- tags ---
        if tagline is None:
            client_attendee=bool(attendee_names(L,i,end) & CLIENT_PEOPLE)
            tags=tags_for(heading, client_attendee)
            tagstr="**Tags:** "+" ".join(tags)
            # insertion point: right after topics line, else after heading(+blank)
            if tline is not None:
                ins=tline+1
                if apply: L.insert(ins, tagstr)
            else:
                ins=i+1
                if ins<len(L) and L[ins].strip()=="": ins+=1
                if apply:
                    L.insert(ins,"")
                    L.insert(ins,tagstr)
            changes.append(("tags",heading,tagstr))
    if apply: open(path,"w").write("\n".join(L))
    return list(reversed(changes))

if __name__=="__main__":
    apply="--apply" in sys.argv
    pat=next((a for a in sys.argv[1:] if not a.startswith("-")),"2026/*.md")
    files=sorted(glob.glob(os.path.join(DAILY,pat)))
    for fp in files:
        for typ,h,val in process(fp,apply):
            print(f"[{os.path.basename(fp)}] {h}\n    {typ}: {val}")
    print("MODE:", "APPLIED" if apply else "DRY RUN")
