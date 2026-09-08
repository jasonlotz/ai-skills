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
DAILY=os.path.join(_resolve_vault(),"@daily-notes")
WEEKDAY={"we","mon","tue","tues","wed","weds","thu","thur","thurs","fri","sat","sun"}

def strip_link(t): return re.sub(r'\[\[|\]\]','',t).strip()
def is_cap_word(t): return bool(re.fullmatch(r"[A-Z][a-z]+", t))

def clean_line(line):
    # strip a leading note-taker timestamp like "Tue, 03 Feb 26 · " (date contains digits)
    m=re.match(r'^(?:[A-Za-z]{3,4},?\s*)?\d{1,2}\s+[A-Za-z]{3,}\s+\d{2,4}\s*[·|]\s*(.*)$', line)
    if m: line=m.group(1)
    # strip any leading bare separator/bullet (e.g. "· names")
    line=re.sub(r'^[\s·•‧∙|]+', '', line)
    parts=[p.strip() for p in line.split(",")]
    parts=[p for p in parts if p!=""]
    # 1) drop obvious junk tokens
    kept=[]
    for p in parts:
        pl=strip_link(p)
        if pl.lower() in WEEKDAY: continue            # weekday fragment
        if "_" in pl or pl.startswith("DL"): continue # distribution list / group alias
        # NOTE: emails and machine usernames are intentionally KEPT. Per Jason, never
        # silently drop an unmatched attendee; map to a known person or leave for later.
        kept.append(p)
    # 2) reversed-duplicate removal + rejoin of "Last, First" pairs
    present={strip_link(p).lower() for p in kept if " " in strip_link(p)}
    out=[]; i=0
    while i < len(kept):
        a=kept[i]; al=strip_link(a)
        b=kept[i+1] if i+1<len(kept) else None; bl=strip_link(b) if b else None
        if b and is_cap_word(al) and is_cap_word(bl):
            full=f"{bl} {al}"                          # reverse: Last, First -> First Last
            if full.lower() in present:
                i+=2; continue                          # reversed dup of an existing full name -> drop both
            else:
                out.append(full); i+=2; continue        # genuine split -> rejoin
        out.append(a); i+=1
    # 3) de-dup exact (case-insensitive, ignore brackets), prefer linked form
    seen={}; final=[]
    for p in out:
        k=strip_link(p).lower()
        if k in seen:
            if p.startswith("[[") and not final[seen[k]].startswith("[["):
                final[seen[k]]=p
            continue
        seen[k]=len(final); final.append(p)
    return ", ".join(final)

def attendee_index(L,i,end):
    for j in range(i+1,min(i+6,end)):
        s=L[j].strip()
        if s=="" or s.startswith("**Topics:"): continue
        if s.startswith("#") or s.startswith("-"): return None
        return j
    return None

def process(fp, apply=False):
    L=open(fp).read().split("\n")
    idx=[i for i,l in enumerate(L) if l.startswith("## ")]
    changes=[]
    for k,i in enumerate(idx):
        end=idx[k+1] if k+1<len(idx) else len(L)
        j=attendee_index(L,i,end)
        if j is None: continue
        new=clean_line(L[j])
        if new!=L[j]:
            changes.append((L[j],new))
            if apply: L[j]=new
    if apply and changes: open(fp,"w").write("\n".join(L))
    return changes

if __name__=="__main__":
    apply="--apply" in sys.argv
    pat=next((a for a in sys.argv[1:] if not a.startswith("-")),"2026/*.md")
    total=0
    for fp in sorted(glob.glob(os.path.join(DAILY,pat))):
        ch=process(fp,apply)
        for old,new in ch:
            total+=1
            print(f"\n[{os.path.basename(fp)}]\n- {old}\n+ {new}")
    print(f"\n=== {total} attendee lines changed ({'APPLIED' if apply else 'DRY RUN'}) ===")
