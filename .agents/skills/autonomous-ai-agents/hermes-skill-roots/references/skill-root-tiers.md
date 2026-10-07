# Skill root tiers — per-condition detail

## Why a skill loads from the profile when you expected the project

Project-local skills load only when all three hold:

1. **cwd sits under a git root** — `find_project_root()` walks up looking for
   `.git`. A directory that is not a repo yields no project root at all.
2. **A `.hermes/skills` or `.agents/skills` directory exists under that root.**
3. **That root is listed in `skills.trusted_project_dirs`.** Trust is what makes
   auto-sourcing from a clone safe, so it is not implied by (1) or (2).

Fail any one and every skill resolves from the profile tier with no warning —
that silence is the usual reason for "why is my project skill ignored?".

`find_project_root()` resolves the **session/terminal** cwd, not the cwd of the
process invoking it. A probe run from elsewhere needs `TERMINAL_CWD` set or it
reports no project root and looks like a dead root.

## Precedence

Lowest tier wins: `project (0) > local profile (1) > skills.create_dir (2) >
skills.external_dirs (3)`.

Inside ONE tier, two different skills sharing a name are **refused as
ambiguous**, never guessed — the entry is addressed by its path relative to the
root (`load_name`), e.g. `research/arxiv`. Cross-tier, the lower-precedence copy
is silently shadowed.

A shadowed copy only logs a warning when the two are **not** byte-identical
(`provably_same_skill`). So a mirrored root is quiet, which is exactly why a
divergent copy is dangerous: it wins at the higher tier with no complaint.

## Quarantine is tier-asymmetric

The prompt-injection scan runs on **project-tier** skills only. A
`verdict=dangerous` entry does not delete the skill — it drops to the profile
tier and keeps loading from there. Expect these in the "resolved below the top
tier" list: they look disappeared but are intact one tier down.

Scripts and skills that legitimately shell out, hit the network or write
credentials trip this scanner hard. That is the price of tier0, not a bug.

## Restoring a root from a backup is usually a regression

Before copying a backup or quarantine tree over a live root, diff it against
the live copy. Live copies carry curation the backup predates:

- descriptions trimmed to the publish cap; backups hold the upstream originals,
  often several hundred characters over it
- examples swapped to project-specific identifiers
- names changed to avoid collisions or to mark ownership

Because the restored root outranks the live one, a verbatim restore **shadows
the curated version** and silently regresses it. Port only what the live root
is genuinely missing.

## Architecture changes must rewrite the criteria that assert them

A validator encodes the architecture as assertions. Moving a root means the
criteria named after the old layout fail — rewrite the criterion to the new
invariant instead of deleting it, so the intent stays checkable. A criterion
that names a path you deliberately changed is a specification conflict, not a
broken test.

## Git hygiene for the skill root

- **Never `git add -A` in the project.** It stages the whole content repo —
  reference PDFs and vendored binaries — not just the skills root. Stage by path.
- Gitignore the noise a live skill root generates: `.hub/` (the skill-hub index
  cache is tens of MB), `__pycache__/`, `*.pyc`, `.curator_backups/`,
  `.curator_ledger.jsonl`.
- A repo whose files are owned by a different account SID refuses every git
  command with `dubious ownership`. Fix once with
  `git config --global --add safe.directory <path>`.