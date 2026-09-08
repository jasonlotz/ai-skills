---
name: ct-ppt
description: Creates a new Cleartelligence-branded PowerPoint presentation (.pptx) based on the Cleartelligence corporate template. Use this skill any time the user invokes /ct-ppt, asks to create a Cleartelligence presentation, starts a new deck for a client, needs slides for a proposal, demo, architecture overview, executive briefing, or any other presentation that should carry Cleartelligence branding. Saves to the appropriate location based on context (project folder, or /home/claude in general chat), then enters a collaborative editing mode. Can accept optional text describing what the deck should cover. Also use when the user says things like "start a deck", "make slides for", "new Cleartelligence presentation", "build a slide deck", or "can you do the slides for" in a professional or client context.
---

# Cleartelligence PowerPoint Creator (ct-ppt)

You are creating a new, professionally formatted PowerPoint presentation using the Cleartelligence
corporate template. Produce a polished deck, save it to the right place, then collaborate with
the user to refine it.

## Two assets: build from the blank, learn from the example

| File | Role |
|---|---|
| `assets/Cleartelligence-blank.pptx` | **Build from this.** Three masters, 27 layouts, zero slides. |
| `assets/Cleartelligence-example.pptx` | **Read this.** 14 slides from a real client deck, one per composition pattern. Never build on top of it. |

**Build on the blank.** It needs no stripping step, is smaller, and — the reason that actually
matters — the example is a real client deck with a named client's content. Building on it and
forgetting to clear the slides ships that client's material inside someone else's deck. The blank
makes that mistake impossible.

```python
prs = Presentation(f"{skill_dir}/assets/Cleartelligence-blank.pptx")   # no clear needed
```

**Reading the example is not optional.** The layouts alone will not tell you how to build a slide.
They carry only the chrome — background, footer, slide number — and expose two to four placeholders
each. Every actual slide design lives in the example: the row of oversized stat figures with
captions beneath, the divider that pairs a section title with a time-box, the content slide that
sets a short category label above a sentence-style headline, the process rows built from aligned
shapes. None of that is reproducible from the layout list.

So open the example, find the slide closest to what you are building, and copy its composition —
the number of elements, their positions, the type sizes, the amount of text per slide. Then build
that arrangement on the blank with `add_textbox` and `add_table`.

```python
ex = Presentation(f"{skill_dir}/assets/Cleartelligence-example.pptx")
for i, s in enumerate(ex.slides):
    print(i, s.slide_layout.name,
          [sh.text_frame.text[:60] for sh in s.shapes
           if sh.has_text_frame and sh.text_frame.text.strip()][:2])
```

If you ever do open the example to build from it, call `clear_sample_slides(prs)` immediately. That
helper drops each slide's relationship as well as its id-list entry — removing only the id-list
entry orphans the slide parts, and the saved file ends up with duplicate zip members that PowerPoint
reports as needing repair.

## Helper scripts

Utilities live in `scripts/ct_helpers.py`. Write your build script in the same directory so the
import resolves:

```python
from scripts.ct_helpers import (add_slide, set_ph, fill_body, add_textbox, add_table,
                                list_layouts, find_layout, clear_sample_slides,
                                NAVY, BLUE, LT_BLUE, ORANGE, WHITE, DARK)
```

Read `ct_helpers.py` before writing any build script.

## Step 1 — Determine save location

**A.** If the user specified a path or filename → use that.

**B.** Cowork project session: `ls /sessions/*/mnt/ 2>/dev/null`. One folder → use it; several → ask;
none → `/sessions/<session-id>/`.

**C.** General chat (no `/sessions` mounts): save to `/home/claude/` and deliver via `present_files`.
Do NOT use `~/Desktop`.

**D.** Running locally (a normal workstation, no `/sessions` or `/mnt`): save next to the related
project files and tell the user the path. Do not invent a container path that does not exist.

## Step 2 — Open the template

Locate the skill directory, then copy `scripts/` next to your build script:

```bash
SKILL_DIR=$(find / -name "Cleartelligence-blank.pptx" -path "*/ct-ppt/*" 2>/dev/null | head -1 | xargs dirname | xargs dirname)
cp -r "$SKILL_DIR/scripts" ./scripts
```

Open the blank (there is no `.potx` — these are normal presentations):

```python
prs = Presentation(f"{skill_dir}/assets/Cleartelligence-blank.pptx")
```

## Step 3 — Layouts: use NAMES, never indices

**The template has three slide masters.** `prs.slide_layouts` exposes only the first, so layouts such
as `Divider Solid` and `End Slide` look like they are missing. `add_slide()` takes a layout **name**
and searches every master. Call `list_layouts(prs)` to see the full inventory.

Layouts worth knowing, with their usable placeholder indices:

| Layout name | Placeholders | Use for |
|---|---|---|
| `1_Title Slide 1` | 10 = headline, 11 = subtitle | Opening slide |
| `Agenda` | 0 = title, 10 = body | Agenda / contents |
| `Divider Solid` | 1, 13 (no title idx) | Section breaks — add text boxes |
| `Section` | 0 = title, 1 = body | Section opener with supporting text |
| `Title and Content` | 0 = title, 1 = body | **The workhorse content slide** |
| `Content - Light Footer` | 0 = title, 1 = body, 11 = footer label | Content with a short category label |
| `Simple` | 0 = title | Title-only slide you compose yourself |
| `Left Image` / `Right Image` | 0 = title, 13 = body | Content beside an image |
| `End Slide` | none | Closing slide |

**Placeholders are sparse by design.** In this template the layouts supply the chrome — background,
footer, slide number — and most content sits in explicit text boxes. Use `set_ph`/`fill_body` where a
placeholder exists, and `add_textbox`/`add_table` for everything else. Call `inspect_slide(slide)`
after adding a slide if you are unsure what is available.

Slide size is 13.33 x 7.5 in (16:9). Keep content inside roughly `left=0.6` to `12.7`, `top=1.4` to
`6.8` to clear the header and footer.

## Step 4 — Build the deck

```python
slide = add_slide(prs, "1_Title Slide 1")
set_ph(slide, 10, "When you trust your data, everything is possible.")
set_ph(slide, 11, "Virginia Pricing Tier — Executive Review")

slide = add_slide(prs, "Divider Solid")
add_textbox(slide, 0.9, 3.0, 8.0, 1.0, "What we found", size=40, bold=True, color=WHITE)

slide = add_slide(prs, "Title and Content")
set_ph(slide, 0, "The rates come from the price sheet, not from history")
fill_body(slide, 1, ["First point", "Second point", "Third point"])

slide = add_slide(prs, "End Slide")
prs.save(out_path)
```

**Every slide needs content.** An empty body looks worse than no slide.

**Deck shape for an executive review** (mirrors the worked example): title → why we're here →
divider → how it works today → divider → what we found → divider → what it means and the options →
what we need from you → closing. Dividers carry a time-box, which keeps a review on schedule.

## Step 5 — Verify before delivering

Re-open the saved file and check three things: every slide has visible content, nothing runs off the
canvas, and the package is clean.

```python
import zipfile, collections
from pptx.util import Emu

prs = Presentation(out_path)
SW, SH = prs.slide_width, prs.slide_height
for i, s in enumerate(prs.slides):
    txt = [sh.text_frame.text.strip() for sh in s.shapes
           if sh.has_text_frame and sh.text_frame.text.strip()]
    tbl = sum(1 for sh in s.shapes if sh.has_table)
    over = [sh.shape_type for sh in s.shapes
            if sh.left is not None
            and (sh.left + (sh.width or 0) > SW or sh.top + (sh.height or 0) > SH
                 or sh.left < 0 or sh.top < 0)]
    flag = "EMPTY!" if not txt and not tbl else (f"OVERFLOW {over}" if over else "ok")
    print(i, s.slide_layout.name, flag)

names = zipfile.ZipFile(out_path).namelist()
dups = [k for k, v in collections.Counter(names).items() if v > 1]
print("duplicate parts:", len(dups), "(must be 0)")
```

**Duplicate parts must be zero.** Any other number means slide parts were orphaned in the package,
and PowerPoint will ask the user to repair the file on open. Build from the blank and this cannot
happen; if it does appear, you opened the example without `clear_sample_slides`.

Then deliver: `present_files` in Cowork, or state the saved path when running locally.

## Step 6 — Collaborate

- "Here's your deck — what would you like to add, change, or reorganize?"
- Suggest logical follow-on slides.
- For edits: `Presentation(path)` → targeted change → save. Do not rebuild from scratch and lose
  edits the user has made in PowerPoint. Check the file's mtime first if unsure.

## What goes in the starter deck

- **Topic described**: title → agenda → divider → 4–6 content slides → closing. Aim for 8–12 slides.
- **Title only**: title + 3 placeholder slides, then ask what belongs on each.
- **Nothing given**: ask — "What's this deck for, and roughly how many slides?"
