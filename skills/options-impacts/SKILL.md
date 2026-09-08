---
name: options-impacts
description: >
  Prepares architectural or strategic discussion notes in Jason's preferred structure: Background,
  Problem Statement, Current State, Desired Future State, Options & Impacts, and (when warranted) a
  Recommendation. Use this skill any time Jason invokes /options-impacts, asks to "prepare notes for
  a meeting," "summarize this for a discussion," "write up the options," or wants a technical or
  strategic conversation turned into a structured document for a client, leadership, or team meeting.
  Also trigger when he says things like "turn this into a doc for the meeting" after a substantive
  technical or architectural discussion. Supports three output formats: Cleartelligence-branded Word
  doc (ct-doc), Cleartelligence-branded PowerPoint (ct-ppt), or plain markdown. Pulls from the current
  conversation as the primary source of content rather than asking Jason to re-explain everything.
---

# Options & Impacts Discussion Notes

This skill turns a substantive discussion (usually technical/architectural, but works for any decision
with real tradeoffs) into structured notes Jason can bring into a meeting. It mirrors how he actually
thinks through these problems: ground the discussion in why it matters, state the problem plainly,
describe what exists today, describe what "better" looks like, lay out the real options with their
tradeoffs, and land on a recommendation only when one is actually warranted.

## Before building

If output format wasn't specified in this request, ask which of the three Jason wants: Cleartelligence-
branded Word doc (ct-doc), Cleartelligence-branded PowerPoint (ct-ppt), or plain markdown artifact.
Don't assume — this varies by audience and all three are in active use.

If the source material is thin (a short ask with no prior discussion in the conversation), ask what
the doc needs to cover rather than inventing content. If there's a rich prior conversation, treat it
as the primary source — don't make Jason re-explain what's already been discussed.

## Structure

### 1. Background
Why this discussion is happening now. Relevant context: what prompted it, what's changed, who's involved
if relevant. Keep this tight — a paragraph or two, not a history lesson. This section earns its place by
orienting someone who wasn't in the earlier conversation, not by being comprehensive.

### 2. Problem Statement
The actual question or tension in one or two sentences. If there are multiple linked questions, state the
primary one and note the others exist. This should be sharp enough that someone could read only this
section and know what's being decided.

### 3. Current State
What exists today, described factually and plainly. Use diagrams, deck content, or prior descriptions
verbatim where they exist rather than paraphrasing loosely — accuracy matters more than elegant prose
here. If parts of the current state are inferred rather than confirmed, say so explicitly (e.g., "the
deck doesn't specify X, but the pattern suggests..."). Never blur assumption into fact.

### 4. Desired Future State
What "better" looks like, in concrete terms tied to the problem statement — not generic aspirations.
If there are multiple candidate future states (e.g., an MVP state and a later V2 state), name both and
be clear about which one this document is actually deciding on.

### 5. Options & Impacts
The core of the document. For each real option:
- **What it is** — one or two sentences, concrete
- **Impacts** — cost, complexity, timeline, risk, operational burden, what it requires that doesn't
  exist today (new skills, new infra, new dependencies)
- **Tradeoffs against the other options** — not just a standalone pro/con list; say what you gain and
  give up relative to the alternatives

Order options by how seriously they should be considered, not alphabetically or by complexity. If one
option is clearly a strawman included only for completeness, say so rather than presenting it as a
peer of the real contenders.

### 6. Recommendation
Include a recommendation whenever the discussion actually supports one — don't hedge for the sake of
seeming neutral. But if the honest answer is "this depends on information we don't have yet" or "this
is a genuine toss-up that needs group discussion," say that plainly instead of forcing a pick. When
there's no clean recommendation, end with the specific open questions or decision points that need to
be resolved before one is possible. A document that surfaces the right unresolved question is doing
its job even without a verdict at the bottom.

## Building the document

**If markdown:** Use standard headers matching the structure above. Tables for option comparisons where
they aid scanning (cost/complexity/risk side by side), prose elsewhere. Save as a markdown artifact.

**If ct-doc:** Follow the ct-doc skill's process (`/mnt/skills/user/ct-doc/SKILL.md`) for template setup,
helper scripts, and save location. Use Heading 1 for the title, Heading 2 for the six sections above.
Use `make_table` for option comparisons and `add_callout` for the recommendation or for flagged
assumptions in Current State. Follow ct-doc's save/present flow.

**If ct-ppt:** Follow the ct-ppt skill's process (`/mnt/skills/user/ct-ppt/SKILL.md`) for template setup,
helper scripts, and save location. Suggested slide mapping (adjust slide count to content density, don't
force one section per slide if it's thin):

| Section | Layout | Notes |
|---|---|---|
| Title | 2 (Starburst) | Doc title + date/meeting name as subtitle |
| Background + Problem Statement | 12 (Title + Content) | Can combine on one slide if both are short |
| Current State | 12 or 15 (2-col) | Use 15 if contrasting current vs. a specific pain point |
| Desired Future State | 12 | |
| Options & Impacts | 20 (3-col) if 3 options, 15 (2-col) if 2, otherwise one slide per option using 13 | This is usually the section that needs the most slides — don't cram all options onto one |
| Recommendation / Open Questions | 28 (Quote/Key Takeaway) if there's a clear recommendation, otherwise 12 with open questions as bullets | Don't force layout 28 if there's no real recommendation — a strong quote-style slide asserting a non-existent conclusion misrepresents the discussion |
| Closing | 34 | |

Keep slide text as scannable bullets, not paragraphs — the full reasoning lives in the markdown/ct-doc
version if one also exists; the deck is for presenting, not reading.

## Content discipline

- Don't inflate this into a comprehensive whitepaper. Pull from the conversation; don't research or
  speculate beyond what's been established unless asked.
- No em-dashes (Jason flags these as feeling AI-generated).
- Keep prose tight — this is a working document for a meeting, not a polished deliverable for a client.
- If the conversation included corrections to earlier assumptions (e.g., "actually, it does X not Y"),
  reflect the corrected version only. Don't surface the wrong path as if it were live context.
