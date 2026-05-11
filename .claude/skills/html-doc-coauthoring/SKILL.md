---
name: html-doc-coauthoring
description: Guide users through co-authoring substantial documentation and produce the final deliverable as a colorful reader-friendly HTML document with a left sidebar nav, charts, cards, tables, flow blocks, timelines, and concise prose. Use when users want to write docs, specs, guides, proposals, PRDs, RFCs, decision docs, onboarding docs, or knowledge-base content and want the result to be easier to read than Markdown.
---

# HTML Doc Co-Authoring

Use this skill to help users create documentation from idea to finished reader-friendly HTML. The main job is co-authoring a useful document; HTML export is the delivery format.

## Offer the workflow

When the user asks to create or improve documentation, offer this workflow briefly:

1. Context gathering: learn audience, goal, source material, constraints, and desired outcome.
2. Structure and co-authoring: build the document section by section with user feedback.
3. Reader testing: check whether a fresh reader can understand and act on the doc.
4. HTML delivery: keep the source JSON in `docs/raw/` and generate the polished `.html` file in `docs/`.

If the user prefers freeform, still use the same quality bar but skip formal stage labels.

## Stage 1: Context gathering

Ask only the questions needed to write the right document:

- What kind of document is this: spec, RFC, PRD, guide, proposal, decision doc, onboarding doc, or something else?
- Who is the primary audience, and what do they already know?
- What should the reader decide, understand, or do after reading?
- What source material should be used: files, notes, code, issue threads, meeting notes, links, or pasted context?
- Are there constraints: tone, template, deadline, confidentiality, offline HTML, branding, or required sections?

Encourage the user to dump context in any format. Read relevant local files when provided. Ask follow-up questions when missing context changes the document's correctness.

## Stage 2: Structure and co-authoring

Create a proposed outline before drafting. Prefer reader-oriented sections such as:

- Executive summary or key takeaways
- Problem / context
- Goals and non-goals
- Proposed approach or main content
- Visual explanation: flow, architecture, lifecycle, timeline, or comparison
- Risks, trade-offs, open questions
- Implementation / next steps
- Appendix for deep details

For each section:

1. Ask focused clarifying questions if needed.
2. Suggest 3-8 points or visuals that could belong there.
3. Let the user keep, remove, combine, or rewrite points.
4. Draft concise content optimized for readers, not for Markdown aesthetics.
5. Iterate using targeted edits rather than rewriting everything.

Capture visual opportunities while drafting. Use:

- Cards for concepts, options, risks, benefits, personas, or feature groups
- Metrics for KPIs, budgets, timelines, counts, and impact
- Tables for comparisons and structured facts
- Cloud infrastructure blocks using Cytoscape.js + dagre for polished AWS/GCP/Azure/topology diagrams
- Flow blocks for process, architecture, lifecycle, and dependencies
- Timeline blocks for roadmap, history, rollout, and milestones
- Chart.js charts for numeric comparisons, trends, distributions, and proportions
- Copyable code blocks for commands, config, API examples, and snippets
- Checklists, resources, and expandable details for user-friendly docs
- Callouts for decisions, warnings, constraints, and action items

## Stage 3: Reader testing

Before final export, review the full document as a first-time reader:

- Is the purpose clear in the first screen?
- Can the target audience understand the key message in under one minute?
- Are assumptions, acronyms, and dependencies explained?
- Are visuals doing real explanatory work?
- Are there contradictions, filler, or missing next actions?

If subagents are available, ask a fresh agent to read the draft and identify ambiguity, missing context, and likely reader questions. Fix issues before export.

## Stage 4: HTML delivery

Use the bundled generator for the final document:

```bash
mkdir -p docs/raw
python3 <skill-dir>/scripts/build_html_doc.py docs/raw/<doc-name>.json
```

Create a compact source JSON file in `docs/raw/`; never intentionally place JSON directly in `docs/`. The script generates `docs/<doc-name>.html` by default and preserves the JSON so the document can be edited and regenerated later. If a JSON file is accidentally passed from `docs/`, the script moves it into `docs/raw/` before generating HTML. The generated page uses a left sidebar navigation layout, Tailwind CSS, Chart.js, and Cytoscape.js topology diagrams from CDNs.

Read `references/html-doc-guide.md` for the JSON schema and block examples.

Default behavior:

- Save source JSON under `docs/raw/` and keep it.
- Never leave JSON files directly under `docs/`; only HTML belongs there.
- Generate HTML under `docs/` with the same base filename.
- Do not paste full HTML into chat.
- Use CDN libraries for Tailwind, Chart.js, Cytoscape.js, and dagre layout.
- Use a left sidebar navigation layout by default.
- Cloud diagrams must look polished and readable; use concise labels, clear groups, and directional connections. Avoid exposing raw diagram syntax as the primary visual.
- Ask before making a fully offline file because it requires larger inline assets.
- Prefer concise prose, scannable layouts, and colorful visual blocks over long Markdown-like sections.

## Completion checklist

- HTML file exists and opens as a reader-friendly document.
- Title, summary, audience, and next actions are obvious.
- Sections are navigable from the left sidebar and visually distinct.
- Charts have labels and data.
- Cloud infrastructure diagrams render successfully and avoid raw syntax errors.
- Code blocks have copy buttons.
- Flow or timeline visuals are easy for non-technical readers to scan.
- The document does not expose secrets or private context unintentionally.

Finish by giving the output path and any caveats only.
