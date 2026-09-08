---
name: ct-doc
description: >
  Creates a new Cleartelligence-branded Word document (.docx) based on the Cleartelligence 2025 corporate template.
  Use this skill any time the user invokes /ct-doc, asks to create a Cleartelligence document, starts a new Word
  doc for a client deliverable, proposal, architecture document, report, or any other professional document that
  should carry Cleartelligence branding. Saves to the appropriate location based on context (project folder, or
  /home/claude in general chat), then enters a collaborative editing mode. Can accept optional text describing what
  the document should contain. Also use when the user says things like "start a new doc", "make a Word document
  for", "new Cleartelligence doc", or "draft a document" in a professional/client context.
---

# Cleartelligence Word Document Creator (ct-doc)

You are creating a new, professionally formatted Word document using the Cleartelligence 2025 corporate template.
The goal is to produce a polished starter document, save it to the right place, and then collaborate with the
user to refine and expand it.

## Helper scripts

Reusable utilities live in `scripts/ct_helpers.py` (relative to this skill's directory). Always write your
build script in the same directory so the import works:

```python
from scripts.ct_helpers import set_cell_bg, add_callout, make_footer, add_subtitle, make_table, NAVY, BLUE, ORANGE
```

Read `scripts/ct_helpers.py` before writing any build script — it contains all brand colors, table helpers,
callout box helpers, and footer helpers.

## Step 1 — Determine save location

### A. If the user specified a path or filename explicitly → use that.

### B. If running inside a Cowork project session:

```bash
ls /sessions/*/mnt/ 2>/dev/null
```

If multiple folders exist, ask the user which one. If only one exists, use it. If none, fall back to
`/sessions/<session-id>/`.

### C. If running in general chat (no /sessions mounts):

Save to `/home/claude/` and deliver via `present_files`. Do NOT use `~/Desktop`.

Name the file based on the document purpose. Use the user's stated name if given.

## Step 2 — Prepare the template

```bash
SKILL_DIR=$(find /sessions /mnt/skills -name "Cleartelligence-2025.dotx" 2>/dev/null | head -1 | xargs dirname | xargs dirname)
DOCX_SCRIPTS=$(find /sessions /mnt/skills -path "*/docx/scripts/office/unpack.py" 2>/dev/null | head -1 | xargs dirname)

cp "$SKILL_DIR/assets/Cleartelligence-2025.dotx" /tmp/ct_base.docx
python3 "$DOCX_SCRIPTS/unpack.py" /tmp/ct_base.docx /tmp/ct_base_unpacked/
sed -i 's|wordprocessingml.template.main+xml|wordprocessingml.document.main+xml|g' \
    "/tmp/ct_base_unpacked/[Content_Types].xml"
python3 "$DOCX_SCRIPTS/pack.py" /tmp/ct_base_unpacked/ /tmp/ct_ready.docx \
    --original /tmp/ct_base.docx --validate false
```

Copy the `scripts/` directory from the skill into your working directory so imports resolve:

```bash
cp -r "$SKILL_DIR/scripts" /home/claude/scripts
```

## Step 3 — Build the document

Write a Python script at `/home/claude/build_doc.py`. Open the template, import helpers, add content:

```python
from docx import Document
from scripts.ct_helpers import set_cell_bg, add_callout, make_footer, add_subtitle, make_table

doc = Document("/tmp/ct_ready.docx")

# Remove empty leading paragraph
for para in doc.paragraphs[:]:
    if para.text.strip() == "":
        para._element.getparent().remove(para._element)
        break

# Title
doc.add_paragraph("Document Title", style="Heading 1")
add_subtitle(doc, "Working Draft  |  April 2026")

# Section
doc.add_paragraph("Section One", style="Heading 2")
doc.add_paragraph("Body text goes here.", style="Normal")

# Callout
add_callout(doc, "Key Point:", "Important note here.")

# Table
make_table(doc, ["Column A", "Column B"], [["Row 1A", "Row 1B"], ["Row 2A", "Row 2B"]])

# Footer
make_footer(doc, "Document Title")

doc.save("/home/claude/output.docx")
```

Then run it:
```bash
cd /home/claude && python3 build_doc.py
```

### Template styles

| Style Name  | Use for               | Appearance                     |
|-------------|-----------------------|--------------------------------|
| `Heading 1` | Major section titles  | Aptos Bold 20pt, navy #182D4F  |
| `Heading 2` | Sub-sections          | 16pt, blue #3364AC             |
| `Heading 3` | Component names       | Aptos Bold 14pt, navy #182D4F  |
| `Heading 4` | Minor callouts        | Italic, light blue #3D8EC8     |
| `Normal`    | Body text             | Aptos Light 11pt, dark #110B18 |

## Step 4 — Save and present

```bash
cp "/home/claude/output.docx" "/mnt/user-data/outputs/output.docx"
```

Then call `present_files` with the `/mnt/user-data/outputs/` path.

## Step 5 — Collaborate

After presenting the file:
- "Here's your starter document — what would you like to add or change?"
- Ask clarifying questions only if the initial prompt was vague
- For subsequent edits, use the Read → Edit → Save cycle on the saved .docx

## What goes in the starter document

- **Topic described** (e.g., "integration architecture for client X"): title + subtitle + intro paragraph + 2–4 placeholder sections
- **Title/filename only**: title + subtitle + intro, then ask what sections they want
- **Nothing given**: ask one question — "What should this document cover?"

Always include:
- Title using `Heading 1`
- Gray italic subtitle / date line
- At least one introductory paragraph
- Footer: "Working draft  |  [Document Title]  |  Cleartelligence" (centered, gray, italic, 8pt)
