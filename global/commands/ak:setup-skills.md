# Setup Skills for This Project

You are helping the user discover and install AI agent skills from https://skills.sh into the current project.

## Step 1: Check Already-Installed Skills

Run to see what's already installed (skip recommending these):

```bash
npx skills list -a claude-code
```

## Step 2: Detect Project Stack

Read the following files if they exist:
- `package.json` — framework, key dependencies
- `requirements.txt`, `pyproject.toml` — Python stack
- `go.mod`, `Cargo.toml` — Go / Rust
- `CLAUDE.md`, `AGENTS.md` — already-documented stack info (prefer this if available)

Summarize the stack in 1-2 lines.

## Step 3: Search for Relevant Skills

Based on the detected stack, run `npx skills find <keyword>` in parallel for relevant keywords. Examples:

- Next.js project → `npx skills find nextjs`, `npx skills find react`
- Python/FastAPI → `npx skills find python`, `npx skills find fastapi`
- TypeScript → `npx skills find typescript`
- General → `npx skills find claude-code`, `npx skills find agent`
- Docker/infra → `npx skills find docker`

Pick 3–5 relevant keywords for this project and run all searches in parallel.

## Step 4: Build Recommendation List

Start with these **default recommendations** based on detected stack (filter out already-installed ones):

**Always recommend (universal):**
- `vercel-labs/skills/find-skills` — meta-skill for discovering more skills
- `anthropics/claude-code` — Claude Code-specific skills and workflows

**TypeScript / JavaScript project:**
- `vercel-labs/skills/typescript-docs` — TypeScript documentation lookup

**Next.js / React / Vue / Svelte (frontend):**
- `vercel-labs/next-skills` — Next.js best practices (if Next.js detected)
- `vercel-labs/agent-skills/web-design-guidelines` — web design guidelines
- `vercel-labs/agent-skills/frontend-design` — frontend design patterns

**General agent / backend:**
- `vercel-labs/agent-skills` — general agent capabilities

Then supplement with results from `npx skills find` searches. Filter out already-installed skills and compile a ranked list. Prefer higher install counts and recognizable owners (vercel-labs, anthropics).

Format each entry as:
```
[N]. owner/repo — description (X installs)
```

Aim for 5–10 total recommendations.

## Step 5: Ask the User

Present the list and ask in a single message:

> Here are suggested skills for **[project name]** ([stack]):
>
> [numbered list]
>
> Enter numbers to install (e.g. `1 3 5`), `all`, or add custom slugs like `owner/repo`.
> Type `none` to skip.

Wait for the user's response.

## Step 6: Install Selected Skills

For each selected skill, run:

```bash
npx skills add <owner/repo> -a claude-code -y
```

The `-y` flag skips confirmation prompts. Install one at a time and report success/failure after each.

If a custom slug fails, tell the user and continue with the rest.

## Step 7: Summary

After all installs:
- List successfully installed skills and their command paths (`.claude/commands/`)
- Note any failures with the error
- Tip: run `npx skills find <keyword>` anytime to discover more skills
