#!/usr/bin/env python3
"""One-shot backfill: walk Staffing Weekly / Pipeline Review / All Hands / Leadership Team /
Practice Directors sections in @daily-notes/2026/ and append any client topics that are
discussed in the body but missing from the section's Topics line.

Idempotent: only appends, never removes. Skips sections without an existing Topics line
(those weren't curated yet -- run link_daily.py for those instead). Use --apply to write."""
import os, re, sys, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import link_daily as L

VAULT = L.VAULT
DAILY = L.DAILY

# Recurring meetings to backfill. Heading must match one of these.
ROSTER = re.compile(r"staffing weekly|all hands|leadership team|practice directors|"
                    r"weekly pipeline|pipeline review", re.I)

def process(path, apply=False):
    text = open(path).read()
    out_lines = text.split("\n")
    idx = [i for i, l in enumerate(out_lines) if re.match(r"^## ", l)]
    changes = []
    for k, i in enumerate(idx):
        end = idx[k+1] if k+1 < len(idx) else len(out_lines)
        heading = out_lines[i][3:].strip()
        if not ROSTER.search(heading):
            continue
        # Find Topics line in section
        topics_line_idx = None
        for j in range(i+1, end):
            if out_lines[j].startswith("**Topics:**"):
                topics_line_idx = j
                break
        if topics_line_idx is None:
            continue
        body = "\n".join(out_lines[i:end])
        existing = set(re.findall(r"\[\[([^\]|#]+)\]\]", out_lines[topics_line_idx]))
        detected = L.detect_topics(heading, body)
        new = [t for t in detected if t not in existing]
        if not new:
            continue
        # Append to Topics line
        old_line = out_lines[topics_line_idx]
        appended = ", ".join("[[" + t + "]]" for t in new)
        new_line = old_line.rstrip() + ", " + appended
        out_lines[topics_line_idx] = new_line
        changes.append((heading, sorted(existing), new))
    if changes and apply:
        with open(path, "w") as f:
            f.write("\n".join(out_lines))
    return changes

def main():
    args = [a for a in sys.argv[1:] if a != "--apply"]
    apply = "--apply" in sys.argv
    if not args:
        print("usage: backfill_roster_topics.py <glob> [--apply]", file=sys.stderr)
        sys.exit(2)
    paths = []
    for a in args:
        paths.extend(sorted(glob.glob(os.path.join(DAILY, a))))
    total = 0
    for p in paths:
        changes = process(p, apply=apply)
        if not changes:
            continue
        rel = os.path.relpath(p, DAILY)
        print(f"\n### {rel}")
        for heading, existing, new in changes:
            total += 1
            print(f"  ## {heading}")
            print(f"      existing: {', '.join(existing) or '(none)'}")
            print(f"      adding:   {', '.join(new)}")
    print(f"\nMODE: {'APPLIED' if apply else 'DRY RUN'}  --  {total} sections updated")

if __name__ == "__main__":
    main()
