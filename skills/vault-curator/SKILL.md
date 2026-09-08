---
name: vault-curator
description: >-
  Curate and maintain Jason's Obsidian vault. Links each daily meeting note to its topic
  hubs, tags it by type, and links known attendees; and keeps the hub notes themselves --
  clients, projects, people, and personal topics (e.g. Core Moto, hobbies, finances) --
  current, with a regenerated "current state", an append-only cited history, live SharePoint
  document links, and status pulled from M365 (Teams/email/SharePoint) and Jira. Use whenever
  Jason adds note-taker output or says "curate", "run the curator", "clean up the vault",
  "update the hubs", "link", "tag", "add backlinks", or points at a file in @daily-notes/;
  also use it to find which notes relate to a client, project, person, or theme. Pulls any Granola meeting notes it has not
  imported yet into the matching daily note as the first stage of a run. Reads an
  entity registry, always confirming before creating notes, renaming, deleting, or overwriting.
---

# Vault curator

## Skill self-update (read FIRST when changing this skill's behavior)

The canonical source is the **ai-skills repo**:
`~/Workspaces/ai-skills/skills/vault-curator/`. Edit the files THERE with Edit/Write.
`~/.claude/skills/vault-curator` and `~/.config/opencode/skills/vault-curator` are symlinks
into it (created by `bash ~/Workspaces/ai-skills/link-skills.sh`), so a change is live in
Claude Code and OpenCode the moment it is saved -- nothing to copy or reinstall. The repo is
git-tracked, so commit the change with a `feat:`/`fix:` message.

**Claude Desktop reads the same folder** (set up and CONFIRMED WORKING 2026-09-08 -- Jason
completed a full vault run in Desktop off the symlink). Its skill store at
`~/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin/<ids>/skills/`
holds a SYMLINK to this repo rather than its own copy, so Desktop, Claude Code, and OpenCode
all resolve to one file and cannot drift. Nothing to rebuild or re-import after an edit.

The one failure mode: a Desktop app update may re-provision that store and replace the
symlink with a fresh private copy. If Desktop starts behaving like an older version of this
skill, that is what happened -- re-run `bash ~/Workspaces/ai-skills/link-skills.sh`, which
re-points any shared skill that reverted (backing up the copy it replaces). As a last resort
`bash bin/build-skill.sh vault-curator` produces a `.skill` archive to import by hand.

**Operating notes for future runs.**

- The entity registry lives at `$ovault/$curator/registry.md` and is writable. Update it
  in-place whenever a new alias, spelling normalization, or hub is confirmed.
- The vault root comes from `$ovault` (already set in Jason's shell); the bundled scripts
  read it themselves, so they run unmodified from this location.
- For person hub title/role enrichment, prefer the MS365 API path first (Outlook email
  search returns sender signatures with titles; SharePoint search can hit company
  directory pages). Fall back to the Teams desktop app via computer-use only when the API
  path can't get there.
- Apply unambiguous spelling normalizations to known hubs WITHOUT asking. See "Cleaning
  the attendee list" below.

---

Jason keeps dense daily meeting notes produced by an auto note-taker (Granola). Each note
holds several meetings and arrives with no links. The curator takes that raw output and
keeps the surrounding structure tidy: it links each meeting to its topic hubs
(clients/projects, curated themes), tags it by meeting type, links the attendees who have
hubs, and creates or maintains the hub notes, so that opening any hub and checking its
backlinks reveals every daily note that touched it.

The workflow it supports: Jason drops in new notes and runs the curator, and it brings
everything into sync without disturbing what he has already written. The note-taker also
gets names wrong constantly, so spotting and fixing those (with confirmation) is part of
the job.

## What "healthy" looks like (the real goal)

Processing notes a few days at a time is the mechanism, not the goal. The goal is a
corpus-wide invariant that each run advances:

1. **Every entity that matters has a hub, and every mention of it is linked across all of
   time** -- not just in the batch being processed. An entity is often a throwaway mention
   in one meeting long before it becomes a real client/project; when that happens you must
   be able to go back and link the early references (see "Candidate log" and promotion).
2. **Every active hub reflects both where things stand now and how it got there** -- a
   regenerated current-state plus an append-only, cited history (see "Hub rollup zones").

So a run has two jobs: curate the new notes, AND keep the corpus healthy (backfill new hubs
into old notes, refresh touched hubs, log candidate entities, fix stale links). The
periodic "health audit" run mode (below) enforces the invariant across the whole corpus.

Hubs are not only clients/projects/accounts. There are also PARTNERS (see below). Jason's
notes are mostly work, but the vault
also has personal topics (e.g. Core Moto, hobbies, Freshline, finances). Those get the same
treatment where it makes sense -- links, and a rollup for anything with an evolving status.
The goal is a healthy VAULT, not just an account tracker.

## Safety model (read first)

The curator runs repeatedly over notes and hubs Jason also edits by hand, so it must never
destroy his work:

- **Additive and idempotent.** Re-running is always safe: already-linked names are not
  double-wrapped, an existing Topics/Tags line is not duplicated, and topics are appended,
  not replaced.
- **Never overwrite Jason's content.** Add the Topics/Tags lines and links to a daily note,
  but do not reformat or rewrite his prose. In hubs, fill blanks and append new facts, but
  never rewrite or delete a value, sentence, or bullet that is already there (see "Updating
  existing hubs").
- **Ask before anything destructive or ambiguous.** Creating a hub, renaming, deleting,
  moving a person between employers, merging duplicates, or resolving a discrepancy (e.g. a
  hub says DoorDash but the email domain says Cleartelligence) all require confirmation.

## Before you start

Read `$curator/registry.md` in the vault. It maps the words that appear in a note (project
names, note-taker misspellings, aliases) to the canonical hub. It is the source of truth,
and the curator owns it: update it on every run whenever a new alias, spelling
normalization, or hub is confirmed, so future runs are automatic and Jason does not have
to confirm the same fix twice. The registry lives in the vault so it is writable from any
session.

### Scope and what counts as "new"

Daily notes live in year folders `@daily-notes/2026/`, `@daily-notes/2025/`,
`@daily-notes/2024/` (a new note may briefly sit loose in `@daily-notes/`). Run the curator
over the notes you want curated, normally the new ones (a date range, this week, or a
single file), not the whole history.

There is no stored "processed" index; the curator decides what is "new" structurally, which
is why re-running is safe:

- An **uncurated meeting** is a `## Heading` section with no `**Topics:**`/`**Tags:**` line.
- A **link to add** is a plain-text attendee name (or body mention) that matches an existing
  hub but is not yet wrapped in `[[ ]]`.
- A **new-hub candidate** is a client/project/person mentioned with no hub yet (surface it).

Scope to new notes rather than re-detecting old ones: a section whose Topics line Jason
removed on purpose looks identical to one never processed, and its keywords could
re-trigger. To backfill a newly created hub into older notes, use the targeted `--add` mode
(below), which adds only that one hub, not a full re-detect.

## Importing from Granola (stage 0 of every run)

The notes originate in Granola, reachable over MCP. A run STARTS by pulling every meeting
that has not been imported yet, so Jason never copies anything by hand.

The Granola tools are deferred -- load them in ONE ToolSearch call:
`select:mcp__claude_ai_Granola__list_meetings,mcp__claude_ai_Granola__get_meetings`.
`list_meetings` takes `time_range` (`this_week` / `last_week` / `last_30_days`) and an
`involvement` filter; use `{captured_by_me: true, listed_as_participant: true}` for "Jason's
meetings". Then `get_meetings` fetches full content, **max 10 ids per call**, so batch.

**What counts as "not imported yet" -- structural, no stored index.** Consistent with the
rest of this skill: a meeting is ALREADY imported when the daily note for its date contains
a `## ` heading matching its Granola title. Everything else is new. This makes re-running
safe and makes a missed day self-healing -- ask for a wider `time_range` and only the gaps
get written.

Route each meeting by its LOCAL start date to `@daily-notes/<year>/<YYYY-MM-DD>.md`. If that
note does not exist, create it from `$templates/daily-note-template.md`:

```
#daily-note

# Daily note - YYYY-MM-DD
```

Append meetings in chronological order by start time, earliest first. Append only -- never
reorder or rewrite meetings already in the file.

### Rendering a Granola meeting into a note section

Granola's `<summary>` is already well-structured prose. Transform it, do NOT re-summarize
it: the body text is Jason's record and paraphrasing it loses detail he relies on.

- **Heading becomes `## <Granola title>`**, verbatim, repairing only garbles the registry
  names. Everything downstream (topics, tags, attendees) keys off this section.
- **Normalize section headings to `###`.** Granola is inconsistent -- most summaries use `#`
  for their top-level sections, some use `###`. Whatever level it used, the meeting's
  sections land at `###` under the `##` heading, with sub-levels shifted to match. Do not
  blindly "demote one level"; that buries an already-`###` summary at `####`.
- **Unescape.** Granola escapes for its own renderer: `\~` -> `~`, `\*` -> `*`, and the XML
  entities `&apos;` `&amp;` `&lt;` `&gt;` arrive literal. Fix all of them.
- **Next Steps: keep the action AND its explainer.** Granola writes each action as a bold
  line plus an indented paragraph of rationale. Keep BOTH, exactly as written -- the
  paragraph carries the why, the owner, and the deadline, and Jason relies on it.
  (Corrected 2026-09-08: an earlier version of this skill dropped the paragraph, inferred
  from older notes that happen not to have one. That was wrong and was never Jason's
  practice. Never strip it.)
- **Watch for a doubled summary.** Granola occasionally emits the same summary twice in one
  `<summary>` block, once at `###` and once at `#` (seen on Staffing Weekly, [[2026-08-31]]).
  Keep ONE copy -- they are the same content at two heading levels, not two sections.
- Leave the rest of the bullets exactly as written.

### Building the attendee line from `known_participants`

The MCP participant list is far cleaner than the pasted-export roster, and it carries EMAIL
DOMAINS -- which is what makes the `#client-meeting` / `#internal-meeting` test in "The Tags
line" reliable rather than a guess. Strip it to bare names, then apply the normal attendee
rules in "Attendee links":

- **Drop Jason himself** (the note creator) -- he is on every meeting and never appears on
  an attendee line.
- **Drop scheduling bots** (`schedule@*.greenhouse.io` and similar), room resources
  (`Conference Room NYC`), and distribution lists (`DL_Portfolio_Leadership`,
  `DL_Practice_Directors`). These are the sanctioned exceptions to "never remove an attendee";
  a bot or a room is not a person.
- **Merge one person appearing under two domains.** Dual-domain orgs list the same human
  twice (`sthompson@counselpress.com` + `sthompson@proceedlegal.com`; `Steven.Joyce@nov.com` +
  `Steven.Joyce@cleartelligence.com`). One entry each.
- **Rejoin `Last, First` renderings** (`Petry, Veronica J` -> Veronica Petry) and drop the
  `from <Org>` suffix and the address itself once the person is identified.
- A CT person appearing under a CLIENT domain is a client-issued account, not a job change --
  employer still comes from their hub folder, per "Hub structure".

Then link the ones with hubs and surface the ones without, exactly as "Attendee links" says.

A meeting whose only participant is Jason is a solo capture (a dictation or a recorded
work session). Import it like any other; it gets topics and tags but no attendee line.

### After importing

The imported sections are now indistinguishable from hand-pasted ones, so the rest of the
run proceeds unchanged: scripts first, then the judgment passes, then hubs and candidates.

## Topics vs tags

Each meeting section gets two annotations on adjacent lines, and they must not be
conflated:

- **Topics** (`**Topics:**` line) are `[[wikilinks]]` to a hub for a specific entity the
  meeting is ABOUT: a client/project (`[[Proceed]]`) or a curated theme
  (`[[Staffing and allocation]]`). People are linked in the attendee list, never on the
  Topics line. The value of a topic link is the backlink.
- **Tags** (`**Tags:**` line) are `#tags` for the TYPE of meeting, not its subject. A tag
  answers "what kind of meeting is this", a topic answers "what is it about."

Rule of thumb: if it names an entity you would want a backlinks hub for, it is a topic; if
it describes the kind of meeting, it is a tag. This is why a routine bi-weekly 1:1 gets no
"performance reviews" topic just because reviews came up; its 1:1-ness is the tag `#1on1`.

```
## Keith Transition Plan w/ Proceed

**Topics:** [[Proceed]]
**Tags:** #client-meeting

[[Ian Rubiano]], [[Keith Meyer]], Scott Thompson
```

## The Topics line

Place it one blank line under the `## Heading`, with one blank line before the attendee
list. Separate multiple topics with commas:

```
## Heading

**Topics:** [[Client or Project]], [[Theme]]

Attendee, Attendee
```

Resolve topics with the registry: match the heading first, then scan the body for trigger
words. Key rules:

- **Projects link alongside their client.** When a meeting is about a specific project,
  link both: a pricing meeting is `[[Proceed]], [[Pricing]]`; a Data Harmony meeting is
  `[[Octapharma]], [[Data Harmony]]`; a DEX / AI-TOC meeting is `[[Proceed]], [[DEX]]`. Each
  project hub lives in its OWN FOLDER at `clients/<Client>/projects/<Project>/<Project>.md`
  and links up to its client (see "Project folders" under Hubs).
- **Every meeting links every client/project discussed in the body.** This includes
  recurring roster/status meetings like Staffing Weekly, Weekly Pipeline Review, All Hands,
  Leadership Team, and Practice Directors. If a client is named in a section header or
  discussed in body bullets (extension, opportunity, bench allocation, status update),
  link it. Themes still apply on top, so Staffing Weekly is always `[[Staffing and
  allocation]]` plus whatever clients came up.
- **Generic initiative words match in the heading only.** "Pricing" and "AI adoption" get
  name-dropped in passing constantly ("spending time on AI adoption", "GPU pricing model"),
  so they only become topics (`[[Proceed]]` / `[[AI adoption bench project]]`) when they are
  in the `##` heading. Specific names (client names, "Data Harmony", "DEX", "data
  governance") are safe to match anywhere, including inside recurring meetings.
- **Curated themes only.** Link a theme only if its hub already exists; do not invent new
  theme hubs.
- **Link partner hubs wherever the platform comes up**, so partner backlinks answer "which
  opportunities involve this platform." Selective partners (`[[Sigma]]`, `[[Vercel]]`,
  `[[Anthropic]]`) link on any substantive mention; ubiquitous ones (`[[Snowflake]]`,
  `[[Databricks]]`) link where the platform is a SUBJECT, not plumbing. See "Partner hubs".
- If a section has no clear topic, leave the Topics line off rather than forcing a weak
  link.

## The Tags line

Place it directly under the Topics line (or under the heading if there is no Topics line).
`#daily-note` stays at the top of the note; per-meeting tags describe the meeting type. Each
section gets one primary type (when the heading indicates one) plus one context tag:

- **Primary type, from the heading:** `#1on1` (X / Jason, 1:1, "and Jason"), `#all-hands`,
  `#leadership` (leadership team, practice directors, leads meeting), `#recruiting`
  (recruiting, role description/alignment, hiring), `#interview` (interview, candidate
  confirmation), `#team-sync` (team leads, bi-weekly, sync-up, tag up, check-in, connect,
  staffing weekly).
- **Context tag, from WHO attended:** `#client-meeting` only if a client-side person
  attended (someone whose hub lives under `clients/<X>/people/`); otherwise
  `#internal-meeting`. This is deliberately attendee-based: a KT, prep, or design session
  about a client attended only by Cleartelligence people is `#internal-meeting`, even with
  `[[Proceed]]` as a topic. It is a client meeting only when a client employee is on the
  attendee line.

```
## Keith + Jason Proceed KT 6        (CT-only attendees -> internal)

**Topics:** [[Proceed]], [[Pricing]]
**Tags:** #internal-meeting

[[Ian Rubiano]], [[Keith Meyer]], [[Lamya Tawfic]], [[Kevin Lazorik]]
```

## Attendee links

The first non-empty line under the heading is the attendee list. (One exception: some
Granola exports put a "Chat with meeting transcript: <url>" line and then a long roster
further down the section; treat that roster the same way.)

Wrap each attendee who has a hub: `Mark McKenna` becomes `[[Mark McKenna]]`. Normalize
note-taker spellings to the canonical hub from the registry (`Venkat` ->
`[[Venkata Vakalapudi]]`, `Matt Richie` -> `[[Matthew Ritchie]]`). Do not link attendees who
have no hub, and never put people on the Topics line. If an unlinked attendee recurs and
seems worth a hub, ask before creating one (Jason does not care about some attendees).

Optionally, link the first mention of a client/project or known person in the body where it
aids navigation ("the [[Proceed]] quote system"). Keep this light: one link per entity per
section.

### Cleaning the attendee list

The note-taker mangles the attendee line, so cleaning it is part of the same pass. Split by
confidence:

**Apply directly (unambiguous):**

- Strip a leading timestamp/separator prefix ("Tue, 03 Feb 26 · Name, Name" or a bare
  "· Name, Name"); the note is already dated.
- Remove distribution lists and group aliases (anything with an underscore or `DL_` prefix,
  e.g. `DL_Practice_Directors`, `account_principals`).
- Remove room/resource entries ("Conference Room NYC", "Microsoft Teams Meeting").
- De-duplicate repeats, including a `Name [C]` co-organizer variant.
- Rejoin obvious comma-split names in First-Last order: "Knight, Brian" -> "Brian Knight",
  "Hewlett, Austin" -> "Austin Hewlett".
- Normalize a name to its canonical hub when the target is unambiguous, without asking:
  "Brian Vandegrift" -> "Brian van de Grift", "Dean A. Misser" -> "Dean Misser",
  "Matt Richie" -> "Matthew Ritchie", "Lamya Tawfik" / "Lamia" -> "Lamya Tawfic",
  "Teradine" -> "Teradyne". This includes body-text occurrences inside the same section,
  not just attendee lines -- spelling normalizations to an existing hub are not a content
  rewrite, they are a wiring fix. Record the alias in the registry the same run so the
  next note arrives already correct.

**Ask first (ambiguous):** a truncated single token that might be a name or a fragment (a
lone "Hari"); a rejoin where you cannot tell first vs last name or whether two tokens are
one person; any case where the target hub itself is in question (not just the spelling).

**Never silently remove an attendee you cannot identify.** Raw emails
(`bani.singh@vercel.com`) and machine usernames (`harikris2105`) are often the only trace of
a real attendee. Map to a known person if you can (link them, drop the redundant token);
otherwise ask Jason or leave the token as-is. Losing an attendee is worse than carrying an
unresolved token.

Batch any questions into one short confirmation rather than interrupting per name.

## Hubs

### Creating new hubs

- **Surface every new client, project, and person; never silently skip one.** Keep a
  running list of entities that look like a client, project, or person but have no hub,
  including one-off and low-confidence mentions. Do not decide on your own that something is
  "just a vendor" or "not worth it": present it and let Jason decide. Group them into one
  batch so the ask is quick.
- **Ask before creating any hub.** After approval, create it from the matching template in
  `assets/templates/` (`person-template.md`, `client-template.md`, `project-template.md`,
  `partner-template.md`).
  When unsure whether something is a client vs a partner/vendor, or which person a
  first-name-only attendee is, ask rather than guess.
- **Apply unambiguous spelling fixes directly; ask only when the target hub itself is in
  question.** Note-taker variants of known hub names ("Teradine" -> Teradyne,
  "Lamya Tawfik" -> Lamya Tawfic) are wiring fixes, not content edits -- apply and record
  the alias. Ask when the question is "is this the same person/entity at all" rather than
  "how is the name spelled."
- When you learn something durable (a project belongs to client X, a name normalizes to Y),
  write it into `$curator/registry.md` the same run.

### Partner hubs (added 2026-07-31; linking broadened 2026-08-03)

Strategic technology partners live in `cleartelligence/partners/<Partner>/`, a PEER of
`clients/` with the same shape: `<Partner>.md` plus a `people/` subfolder for partner-side
staff, and the same full rollup treatment as a client hub (Current state, Open threads,
History, Documents). Build them from `partner-template.md`. The linker auto-discovers
`partners/*/people/`, so a partner-side person becomes linkable as soon as their hub exists.

This replaces the older "tools and platforms are not topics" rule for partners CT actually
holds. **Link the partner wherever the platform comes up** -- the point of these hubs is that
their backlinks answer "which opportunities involve this platform." Calibrate by how common
the name is:

- **Selective partners** (`[[Sigma]]`, `[[Vercel]]`, `[[Anthropic]]`) -- link on any
  substantive mention. They appear in a manageable share of notes, so full linking keeps
  the backlink list useful.
- **Ubiquitous partners** (`[[Snowflake]]`, `[[Databricks]]`) -- link where the platform is
  a SUBJECT: a selection or evaluation, demo, POC, migration, cost/licensing, certification,
  partnership or summit news, an opportunity. Skip pure plumbing ("the data lands in
  Snowflake", "their warehouse is Databricks"). These two underpin most engagements; linking
  every passing mention puts them on two-thirds of all meetings and their backlinks stop
  discriminating.

Before mass-linking a NEW partner, count its mentions first
(`grep -rlw <Partner> @daily-notes/<year>/`). Under roughly a third of notes, link every
mention; above that, apply the subject test and record which rule applies in the registry.


A partner hub earns its keep through two sections a client hub does not have: **Patterns and
methodology** (reusable techniques from training/delivery, applicable on the next
engagement) and **Where <Partner> shows up** (every account touching the platform, including
the cautionary cases where it was mis-sold). Keep CT's POSITION on the product current —
what it is right for and what it is not — since that is what prevents the next bad fit.

Current partner hubs: `[[Sigma]]`, `[[Snowflake]]`, `[[Databricks]]`, `[[Vercel]]`,
`[[Anthropic]]`.

**Partners can own projects, the same way clients do.** `[[Anthropic Certification]]` is not
a separate thing from the `[[Anthropic]]` partnership -- partner tier is gated on certified
headcount, so the cert rollout is the workstream that earns the partnership. Link both on a
cert-rollout meeting: the project carries the rollout detail, the partner carries the status
it advances. When a partner hub has a workstream like this, give the partner hub a
`## Projects / workstreams` section and add a `**Partner:**` field to the project note, so
the relationship reads in both directions.

Only create a partner hub for a partnership CT actually holds. A partner of a CLIENT (e.g.
Kin Analytics, Tokyo Century's AI partner) is context for that client's hub, not a CT
partner hub, unless CT engages them directly.

### Project folders (changed 2026-08-04)

**Every project gets its own folder**, holding a same-named hub note. This applies to client
projects, Cleartelligence internal projects, and partner-owned projects alike:

```
clients/<Client>/projects/<Project>/<Project>.md     e.g. clients/Proceed/projects/Pricing/Pricing.md
cleartelligence/projects/<Project>/<Project>.md      e.g. projects/Practice Plan - 2026/Practice Plan - 2026.md
```

The point is that supporting material -- decks, diagrams, exports, working docs -- lives
beside the hub instead of scattering. When creating a project hub, create the folder in the
same step; never drop a bare `<Project>.md` into a `projects/` directory.

Obsidian resolves `[[wikilinks]]` by filename, so the nesting has no effect on linking and
existing links survive the move. The one thing to protect is filename uniqueness: two notes
with the same name anywhere in the vault make `[[That Name]]` ambiguous, so keep project
names globally distinct (prefer `[[HBP Finance]]` over a bare `[[Finance]]`).

### Hub structure

Each hub follows its template: a header of labeled fields (left blank when unknown, for
Jason to fill later), a `## Summary` grounded strictly in the daily notes, and for people a
`## Personal` block (location/family/hobbies, only when the notes mention them). A person's
`**Employer:**` comes from the folder (`cleartelligence/people/` = Cleartelligence;
`clients/<X>/people/` = that client). Titles are left blank to be looked up from Teams.
Never fabricate.

### Hub rollup zones (current state + history)

Beyond the template's static `## Summary` (what the entity IS), every active client/project
hub carries maintained zones so "where do things stand" is a single read, not a backlink
chase:

- A header marker `**Last rolled up:** <date> (notes through [[<date>]]; <other sources>)`.
  A hub is stale (needs regenerating) when it has backlinks or source signals newer than
  this marker.
- `## Current state` -- a REGENERATED 3-6 sentence synthesis of where the entity stands
  now: focus, status, open threads, key people. This is the answer, and being regenerated
  each run (not hand-maintained) means it never drifts.
- `## Open threads` -- what's in flight, each line stamped with the meeting/source it's
  current as of. Close a thread by moving it into History when it resolves.
- `## History` -- APPEND-ONLY, one line per meeting (or source event), newest first, every
  line citing its source. This is the auditable ledger; never rewrite or delete a line.
- `## Documents` -- live links to the SharePoint/Office files for this entity that Jason is
  actually working with, as `[title](<url>)` (angle brackets around URLs with spaces). See
  "Multi-source status" for how these are found; refreshed each run, deduped, HR/personal
  files excluded.

**Provenance tags make the rollup trustworthy.** Tag every History / Open-thread line with
its source: `[[YYYY-MM-DD]]` for a daily note, `(Teams YYYY-MM-DD)` / `(email YYYY-MM-DD)` /
`(SharePoint <doc>)` / `(Jira <TICKET>)` for other sources. Mark anything not explicitly
confirmed as inferred, and surface it rather than assert it.

Only maintain rollup zones for hubs worth the upkeep; regenerate only the hubs a run
actually touched (new notes or a source sweep), keyed off `Last rolled up` -- never rebuild
every hub every run.

### Updating existing hubs (the balance)

Keep improving hubs as new notes arrive, but treat Jason's content as owned. The rule is:
**add where there is a gap, ask where there is a conflict, never rewrite what is already
written.**

- **Additive only.** Never overwrite, rephrase, reorder, or delete an existing field value,
  summary sentence, or bullet.
- **Fill blanks.** Populate an empty field or an empty `## Summary` from the notes. This is
  the main way a hub gets richer over time.
- **Append new facts.** A substantive new fact becomes a new bullet under the relevant
  section, leaving existing lines untouched. Do not rewrite an existing Summary paragraph;
  if the new information is bigger than a bullet, propose it.
- **Surface conflicts.** If a note contradicts the hub (a role change, a status flip, an
  employer correction), do not edit over it; flag it ("hub says X, recent notes say Y,
  update?") and let Jason decide.
- **Idempotent.** If nothing new is learned, change nothing.

### Create the hub first, then relink

A link only produces a backlink if its target exists, so the order is: create the hub, then
relink the notes that mention it.

1. While scanning, collect entities needing a hub and get approval.
2. Create the approved hubs and add them to `$curator/registry.md`.
3. Relink the affected notes so the now-existing hubs pick up their backlinks (linking is
   idempotent, so this is safe).

The same loop runs across sessions: when a brand-new client or person first appears later,
create the hub then and relink the earlier mentions. Do not leave a mention unlinked just
because the hub did not exist when the note was first processed.

Backfill is targeted, and works the same for people and topics:

- A new **person** hub backfills automatically on any relink, because attendee linking is an
  exact name match: the linker wraps that name wherever it still appears plain.
- A new **client/project** hub backfills via `link_daily.py --add "Hub Name"`, which adds
  `[[Hub Name]]` only where its name literally appears, appending to existing Topics lines.

Both are additive and idempotent, and neither re-runs full topic detection, so removed
topics and keyword false positives are not re-introduced. (A topic whose subject is not its
literal name, e.g. a section that says "pricing" but not "Proceed", is matched by its
registry rule on the first pass, not by `--add`; for those, review the matches by hand.)

## Candidate log (the promotion problem)

A random one-off mention often becomes a real client/project weeks later, and the pain is
having to remember it existed and dig up the early references. Solve it by logging, not
remembering:

- `$curator/candidates.md` records every surfaced-but-not-yet-hubbed entity (client,
  project, person) with the note(s)/date(s) it appeared in. Append new sightings every run;
  never silently drop one.
- **Promotion:** when Jason approves a candidate (or the health audit flags one that has
  crossed a "mentioned in N meetings / recurring" threshold), create the hub, then link its
  already-logged occurrences and seed the hub's History from those dated mentions. Because
  the sightings were logged as they happened, this is a link-up, not an archaeology dig.
- **Oblique early references** (e.g. "the media company Dustin referred" before it was named
  "Truform") won't match a literal-name backfill. At promotion time ONLY, do one LLM sweep
  of earlier notes for plausible references, confirm with Jason, then link. This is the one
  place semantic search earns its keep -- not routine querying.

Keep the human gate on hub CREATION; the candidate log makes eventual promotion cheap
without forcing hub sprawl.

## Multi-source status (M365 + Jira)

Daily notes capture what was DISCUSSED; the events that actually change a project's status
-- a win/loss, an SOW or contract signed, budget approved, a start or go-live date, an
escalation, a departure -- usually land in email or Teams (and dev status lives in Jira),
never in a meeting note. So refreshing a hub's status often means pulling those sources.

For a hub being refreshed (touched this run, or in the health audit), sweep since its
`Last rolled up` date:

- **Scope by the hub's entity + its key people** (registry has aliases/emails). Filter by
  participants, not just the name -- short client names (e.g. "NOV") pull date noise
  ("Nov 13") otherwise.
- **Teams first, email selectively.** Internal status lives in Teams chat; email is mostly
  noise except external client confirmations and shared docs. Use `chat_message_search`,
  `outlook_email_search` (scoped by sender/recipient), and `sharepoint_search` for docs.
- **Extract STATE CHANGES only**, not chatter. Write each to `## History` with its source
  tag, close any resolved `## Open threads`, then regenerate `## Current state`.
- **System of record vs. signal.** Win/loss, stage, and contract dates are most
  authoritative in the CRM (Salesforce) / NetSuite; dev/ticket status is authoritative in
  Jira. Prefer those for hard facts; use email/Teams for the qualitative "what was decided /
  what's blocked." A wrong "we won" is worse than a gap -- confirm before asserting.
- **One sweep can update several hubs.** Route each finding to the right hub, not just the
  one you searched for.
- **Privacy.** Keep HR/comp/personal-sensitive content out of hubs you might share; capture
  the professional substance, not private detail or emotional quotes.

**Documents (the `## Documents` hub zone).** Link the SharePoint/Office files Jason is
actually WORKING WITH for an entity -- not every file that happens to match the client name.
There is no "recently opened by me" tool, so use the docs that reach him as the signal:
files shared in his Teams chats / meeting chats and email attachments for that entity (e.g.
the NOV rate card surfaced via Teams). Use `sharepoint_search` (and the client's dedicated
account site/folder when one exists, e.g. `sites/Accounts-<Client>-...` or `.../Account
Files/Portfolio <X>/<Client>/`) only as a fallback for the current canonical version. Then:
dedupe copies (v1/v2/"- Copy"), keep the meaningful few, EXCLUDE anything HR/performance/
comp/personal, and write each as `[title](<webUrl>)`. Refresh the list each run.

The M365 tools (`outlook_email_search`, `chat_message_search`, `sharepoint_search`,
`sharepoint_folder_search`, `teams_list_chats`, `read_resource`, `get_me`) are deferred --
load via ToolSearch. If the connector is disconnected, say so and continue notes-only rather
than guessing.

## Run modes

- **Incremental tick** (the normal run, a few days at a time): curate the new notes
  (clean/link/topics/tags), then for each hub those notes touched, append History +
  regenerate Current state (optionally with an M365/Jira sweep), and append any new
  candidate sightings.
- **Health audit** (periodic, whole corpus -- weekly-ish or on request): unresolved links,
  candidates that crossed the promotion threshold, hubs with stale rollups (backlinks newer
  than `Last rolled up`), name variants not yet in the registry, and uncurated old meetings.
  This keeps the corpus healthy despite incremental ingestion, and it's the mode for a
  "clean up as far back as we can" pass.

## Bundled scripts

Three scripts in `scripts/` encode the deterministic parts. They read the live vault, are
additive/idempotent, and take a glob (relative to `@daily-notes/`); add `--apply` to write,
omit it to dry-run. Keep their dictionaries in sync with `$curator/registry.md` in the
vault (the registry is the source of truth). The scripts locate the vault automatically and
no longer hardcode a per-session mount path: they read the vault root from an environment
variable (`$ovault`, Jason's existing one, is checked first, then `OVAULT`/`VAULT`/
`OBSIDIAN_VAULT`) as long as it points at a folder containing `@daily-notes/`, otherwise
they auto-detect by
scanning the mounted folders for the one containing `@daily-notes/`, and finally fall back
to the script's own `../../../..` (the vault root when installed under
`vault/.claude/skills/`). If detection ever fails (e.g. multiple vaults mounted), run with
`VAULT=/path/to/vault python3 scripts/<name>.py ...` to pin it explicitly.

- `link_daily.py` — inserts the `**Topics:**` line and links attendees. It auto-discovers
  people from every `people/` folder, so a hub becomes linkable as soon as it exists. The
  Topics line is only inserted where a section has none; it is never re-detected into an
  existing one. `--add "Hub Name"` is the targeted backfill of a single new hub.
- `augment.py` — appends project hubs to existing Topics lines and adds the `**Tags:**` line
  (meeting-type plus attendee-based context).
- `clean_attendees.py` — the attendee-line cleanup (timestamps, distribution lists,
  duplicates, "Last, First" rejoins).

Typical order for a fresh batch (omit `--apply` on any step to dry-run):

```
python3 scripts/clean_attendees.py "2026/2026-06-*.md"          # clean attendee lines
python3 scripts/link_daily.py     "2026/2026-06-*.md" --apply   # topics + attendee links
python3 scripts/augment.py        "2026/2026-06-*.md" --apply   # project links + tags
```

(After creating a new client/project hub, also run `link_daily.py "<scope>" --add "Hub
Name" --apply` to backfill it into older notes.)

The scripts are a fast first pass, not a replacement for judgment: they do not ask about
new entities, name fixes, or hub summaries. Do those steps by hand around them.

## Verifying a run

- Every `[[link]]` resolves to an existing `.md` (in `cleartelligence/`, its subfolders, or
  `personal/`). An unresolved link usually means a spelling slipped past the registry; fix
  it or add the alias.
- Each meeting heading has exactly one Topics line (when it has a topic) and one Tags line,
  in that order, before the attendee line.
- Spot-check a hub's backlinks (in Obsidian, or by grepping `[[That Hub]]` across
  `@daily-notes/`).
- For touched active hubs: exactly one `## Current state` and one `## History`, the
  `Last rolled up` marker advanced, and every History/Open-thread line carries a source tag.
- New candidate sightings appended to `$curator/candidates.md`; no surfaced entity dropped.

Report a short summary: notes processed, links and tags added, hubs created or updated,
names fixed, and any questions for Jason.

## Going forward

New notes arrive with no links; running the curator on them is the maintenance step. It is
reasonable to offer Jason a scheduled run (e.g. weekly) that curates the past week's notes
and surfaces any new entities, name issues, or hub conflicts for him to confirm.

A weekly scheduled run should do both jobs: an incremental tick on the past week's notes,
plus a lightweight health-audit pass (stale rollups, promotable candidates, unresolved
links). Keep active hubs' Current-state fresh via M365/Jira source sweeps so "where do
things stand on X" is always a one-read answer rather than a backlink chase.
