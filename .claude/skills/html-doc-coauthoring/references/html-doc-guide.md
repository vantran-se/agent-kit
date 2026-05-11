# HTML Co-Authored Document Guide

Use this reference only during final HTML delivery after the document content and structure are agreed with the user.

## JSON spec shape

Convert the approved draft into a compact JSON file under `docs/raw/`, then pass it to `scripts/build_html_doc.py`. The generated HTML goes to `docs/` with the same base filename. Do not intentionally place JSON directly in `docs/`; the generator will move accidental `docs/*.json` inputs into `docs/raw/`.

```json
{
  "title": "Document title",
  "subtitle": "Optional one-line context",
  "audience": "Who should read this",
  "summary": "Short executive summary",
  "theme": "slate",
  "toc": true,
  "badges": ["RFC", "Draft"],
  "actions": [
    {"label": "Approve proposal", "href": "#decision"}
  ],
  "sections": [
    {
      "title": "Section title",
      "intro": "Optional short intro",
      "blocks": []
    }
  ]
}
```

All fields are optional except `title` and `sections`. Keep strings concise. Use Markdown only inside `markdown` blocks when needed. The HTML layout uses a left navigation sidebar by default.

## Block types

### Markdown

```json
{"type": "markdown", "content": "Short prose, bullets, or numbered steps."}
```

Use for normal text. Keep paragraphs short.

### Cards

```json
{
  "type": "cards",
  "columns": 3,
  "items": [
    {"title": "Fast onboarding", "body": "New users can scan the flow quickly.", "badge": "Benefit"},
    {"title": "Token efficient", "body": "The generator expands compact JSON into UI."}
  ]
}
```

Use for features, risks, options, responsibilities, or takeaways.

### Metrics

```json
{
  "type": "metrics",
  "items": [
    {"label": "Setup time", "value": "5 min", "hint": "Typical path"},
    {"label": "Docs", "value": "12", "hint": "Current backlog"}
  ]
}
```

Use for numeric facts or memorable signals.

### Table

```json
{
  "type": "table",
  "headers": ["Option", "Pros", "Cons"],
  "rows": [
    ["HTML export", "Readable and visual", "Needs browser"],
    ["Markdown", "Simple diff", "Harder to scan"]
  ]
}
```

Use for comparisons and structured information.

### Callout

```json
{"type": "callout", "tone": "warning", "title": "Constraint", "content": "Do not inline large libraries unless offline export is required."}
```

Tones: `info`, `success`, `warning`, `danger`.

### Cloud infrastructure diagram

```json
{
  "type": "cloud",
  "title": "Production architecture",
  "provider": "AWS",
  "groups": [
    {"id": "vpc", "title": "VPC"},
    {"id": "private", "title": "Private Subnet", "parent": "vpc"}
  ],
  "nodes": [
    {"id": "web", "label": "Web API", "type": "api", "group": "vpc"},
    {"id": "db", "label": "Postgres", "type": "database", "group": "private"},
    {"id": "cache", "label": "Redis", "type": "cache", "group": "private"}
  ],
  "connections": [
    {"from": "web", "to": "db"},
    {"from": "web", "to": "cache"}
  ]
}
```

Use for cloud topology and CI/CD deployment diagrams. This renders with Cytoscape.js and dagre via CDN for a polished topology graph. Keep labels short, use `groups` for boundaries like VPC, region, subnet, project, cluster, or account, and use `type` values such as `internet`, `client`, `load-balancer`, `api`, `server`, `function`, `database`, `cache`, `queue`, `storage`, `security`, `observability`, and `ci`.

### Flow

```json
{
  "type": "flow",
  "title": "Reader flow",
  "items": [
    {"title": "Open doc", "body": "Start with a clear hero summary."},
    {"title": "Scan visuals", "body": "Use cards, tables, and charts to find the point quickly."},
    {"title": "Take action", "body": "Follow clear next steps."}
  ]
}
```

Use for workflows, architecture, lifecycles, handoffs, and dependencies. It renders as friendly cards instead of technical diagram syntax.

### Timeline

```json
{
  "type": "timeline",
  "title": "Rollout plan",
  "items": [
    {"date": "Week 1", "title": "Draft", "body": "Collect context and align on structure."},
    {"date": "Week 2", "title": "Review", "body": "Test with readers and fix gaps."},
    {"date": "Week 3", "title": "Publish", "body": "Deliver the HTML page."}
  ]
}
```

Use for roadmaps, rollout plans, histories, milestones, and schedules.

### Chart.js chart

```json
{
  "type": "chart",
  "chartType": "bar",
  "title": "Adoption by team",
  "labels": ["Core", "Platform", "Apps"],
  "datasets": [
    {"label": "Docs", "data": [8, 5, 12]}
  ]
}
```

Supported types depend on Chart.js: `bar`, `line`, `pie`, `doughnut`, `radar`, `polarArea`. Use charts only with real or clearly labeled example data.

### Steps

```json
{
  "type": "steps",
  "items": [
    {"title": "Gather context", "body": "Collect audience, goal, constraints, and source material."},
    {"title": "Co-author sections", "body": "Draft, review, and refine the content with the user."},
    {"title": "Deliver HTML", "body": "Run the generator and verify rendering."}
  ]
}
```

Use for procedures, rollout plans, and implementation paths.

### Code

```json
{"type": "code", "language": "bash", "content": "python3 scripts/install.py"}
```

Code blocks render with a copy button. Use for exact commands, config, API examples, or snippets.

### Checklist

```json
{
  "type": "checklist",
  "title": "Launch readiness",
  "items": [
    {"label": "Secrets moved to env vars", "checked": true},
    {"label": "Rollback plan documented", "body": "Link the runbook before release."}
  ]
}
```

Use for release readiness, acceptance criteria, migration tasks, and review gates.

### Resources

```json
{
  "type": "resources",
  "title": "Useful links",
  "items": [
    {"label": "Runbook", "href": "./runbook.html", "description": "Operational steps and rollback."}
  ]
}
```

Use for links, references, related docs, dashboards, tickets, or source files.

### Details / accordion

```json
{
  "type": "details",
  "title": "Deep dives",
  "items": [
    {"title": "Why not option B?", "body": "Option B adds operational complexity without improving reliability."}
  ]
}
```

Use for optional depth without overwhelming casual readers.

## Design guidance

- Prefer one strong hero summary and 3-6 sections.
- Start with what the reader needs to know, not background.
- Use cloud blocks for infrastructure, flow blocks for relationships, timelines for milestones, and charts for numbers; avoid decorative visuals.
- Add enough color accents to guide scanning, but keep the page professional.
- Keep each section scannable: one intro, then visual blocks.
- Use tables when readers need exact comparisons.
- Use callouts sparingly for decisions, risks, and constraints.
- If content is long, add a final appendix section.

## Output behavior

- Write source JSON to `docs/raw/<doc-name>.json` after co-authoring is complete.
- Run `python3 <skill-dir>/scripts/build_html_doc.py docs/raw/<doc-name>.json`.
- Keep the JSON file for future edits and regeneration.
- The generated HTML should be `docs/<doc-name>.html`.
- If `docs/<doc-name>.json` exists, move it to `docs/raw/<doc-name>.json` or run the generator once to normalize it.
- Do not print the generated HTML in chat.
- Tell the user both the JSON source path and HTML output path.
