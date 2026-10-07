---
name: hermes-skill-roots
description: Use when Hermes skills load from the wrong place.
---

# Hermes skill roots: tiers, trust, and safe restructuring

Skills resolve from **several roots at once**, and a silent precedence rule
decides which copy actually runs. Almost every "my project skill is being
ignored" or "my edit had no effect" report is a root/tier problem, not a
missing file.

## When to Use

- a skill loads from a location you did not edit
- `skill_view` refuses with "Ambiguous skill name"
- you are moving, merging, splitting or restoring a skill root
- you are adding a skill and need to know which directory actually gets scanned
- git hygiene for a directory that *is* a skill root

## Diagnose before changing anything

Run `scripts/verify_skill_roots.py` rather than inferring. It prints project
root, trust, every root with its tier, resolved status per entry, anything
falling back to a lower tier, and byte-drift between roots.

## The three preconditions for project-tier skills

A project-local skill loads only when **all three** hold:

1. the effective cwd sits under a **git root** (`find_project_root()` walks up
   for `.git`) — a non-repo directory has no project tier at all
2. a `.hermes/skills` or `.agents/skills` directory exists under that root
3. that root is listed in `skills.trusted_project_dirs` (trust is what makes
   auto-sourcing from a clone safe, so it is never implied)

Missing any one fails **silently** — every skill falls back to the profile tier
with no warning. Check all three before concluding a root is dead.

## Precedence and conflicts

`project (0) > local profile (1) > skills.create_dir (2) > external_dirs (3)`.

- **Same name, same tier** → refused as `ambiguous`, addressed by path relative
  to the root (`research/arxiv`). Never guess.
- **Same name, different tiers** → the lower one is shadowed, silently.
- The shadow **warning fires only when the two files differ**. Byte-identical
  copies are quiet, which is exactly why a divergent copy at the higher tier is
  dangerous: it wins with no complaint.

`references/skill-root-tiers.md` has the per-condition detail and the
quarantine behaviour.

## Procedure for restructuring a root

1. **Diff before copying.** Compare the candidate source against the live copy.
   Live copies usually carry curation the source predates — descriptions trimmed
   to the publish cap, examples swapped to project identifiers, names changed to
   break collisions.
2. **Never restore a root verbatim.** The restored root outranks the live one, so
   upstream originals shadow the curated version and regress it without
   warning. Port only what is genuinely missing.
3. **Ensure the preconditions** — git root, the skills subdir, the trust entry.
   If the project is not a repo, `git init` is the enabling step, not a
   workaround.
4. **Keep a mirror if other sessions depend on it.** The profile tier is the
   fallback for sessions whose cwd is elsewhere; mirror byte-identically.
5. **Re-run the probe:** zero drift, zero `ambiguous`, nothing unexpectedly
   falling back.

## Rewriting the checks that describe the old layout

When an architecture change invalidates an assertion that names the old path —
a validator criterion, a CI check, a doc table — rewrite the assertion to the
new invariant. Do not delete it: a criterion naming a path you deliberately
changed is a specification conflict, and deleting it trades a loud failure for a
silent one.

## Pitfalls

- **The injection scan is tier-asymmetric.** It runs on project-tier skills
  only. A `dangerous` verdict does not delete anything — the entry drops to the
  profile tier and keeps loading from there, so it reads as disappeared while
  staying intact. Anything that shells out, hits the network or handles
  credentials will trip it; that is the price of tier0, not a bug.
- **Never `git add -A` in a content repo.** It stages the whole corpus — vendored
  binaries and reference documents — not the root you were working on. Stage by
  path. If you over-stage, `git reset` immediately and say so.
- **Gitignore the noise a live skill root generates:** the skill-hub index cache
  (`.hub/`, tens of MB, written by Hermes itself), `__pycache__/`, `*.pyc`,
  curator backup dirs and ledgers.
- **A repo owned by a different account SID refuses every git command** with
  `dubious ownership`. Fix once with
  `git config --global --add safe.directory <path>`.
- **Scan roots recursively.** `<category>/<name>/SKILL.md` is normal Hermes
  layout, so a flat listing undercounts badly.
- **Editing a lower-tier copy is wasted work** — the next sync overwrites it.
  Edit the authoritative root and propagate downward.

## Verification standard

Report the probe's actual numbers — roots and tiers, loadable count, ambiguous
count, drift count — not a narrative of the moves. A restructuring is done when
drift is zero and nothing resolves ambiguously.