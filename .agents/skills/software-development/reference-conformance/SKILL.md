---
name: reference-conformance
description: Reproduce a known-correct reference output exactly.
---

# Reference Conformance

The target is **known-correct** (user-provided ground truth), so you are not hunting an unknown root cause — you are reconciling the code's output to a spec. For finding an *unknown* bug, use `diagnosing-bugs` (its red-loop and root-cause phases apply). Here the loop is against a *given* target, and the hard part is usually what happens to the rest of the suite after you change a default.

## Phase 1: Build a red/green checker against the reference

Write a script that asserts the **exact** known-correct values — every field the user gave (positions, aspects, speeds, counts, ordering) — not "runs without erroring." It must:

- Drive the **same code path the real app uses** (the app's default builder/config), so green means the app is actually fixed, not just the harness.
- Print a per-field PASS/FAIL and exit non-zero on any mismatch, so it goes red on the discrepancy and green when reproduced.
- Be deterministic (pin time, seed RNG, isolate filesystem, freeze network).

Run it. It should be red on the discrepancy. This is the loop; everything else consumes it. No red-capable checker, no fix.

**Validate the checker against a known-good input first.** Push the reference (or any input whose correct output you already trust) through the same checker. If it does not come out exact, the checker is broken, not the code — fix the checker before believing any mismatch it reports. Three defects cause nearly all broken checkers:

- **Reimplemented the rule under test.** Writing your own version of a function you are comparing against encodes rules the real function does not have, and the diff reads as a confident, entirely fictional finding. Call the real function and filter its output; justify any post-filter against the function's own source or docstring.
- **Synthetic inputs.** A hand-picked angle, date, or separation that "should" produce no match proves nothing. Drive real data from a real case; an empty result on an arbitrary value is not evidence of a bug.
- **Cross-layer identifiers.** The same concept is named differently per layer (e.g. `conj`/`sq` vs `Conjunction`/`Square`). Un-normalised comparison yields a wall of phantom diffs that reads as catastrophic failure. Normalise identifiers, then compare.

A checker that cannot reproduce a result you already trust has no standing to report a mismatch. Full drill — the three defects that cause nearly all broken checkers, severity-honesty guidance, ledger discipline, and retraction wording — in [references/validate-comparison-harness.md](references/validate-comparison-harness.md).

## Phase 2: Fix until green

Change one variable at a time, re-running the checker after each. Typical causes when reproducing a reference: a wrong **default** (node type, orb table, threshold), a wrong **scope** (which objects are included/excluded), or a wrong **derivation**. Confirm each fix against the checker, not by eyeballing output.

## Phase 3: Triage the full suite

A fix that changes a **default or behavior** makes the whole suite go red in places you did not touch. Run the **full** suite, then classify every new failure:

- **Stale assertion** — the test encodes the old (now-wrong) behavior. Update it to the corrected value.
- **Genuine regression** — the fix broke something real. Investigate; **never** edit the test to make it pass.
- **Contested lock-file** — a table/config literal disagrees with live behaviour while the *behavioural* tests pass. The code is probably right and the lock stale, but that is a judgement to confirm with the user, not to settle silently: report both sides, name each one's source of truth, and ask before propagating. Editing a red lock to make the suite green cements whichever value lost.

They look identical in the red output. The only discriminator: **does the assertion's expectation match the intended (known-correct) behavior?** When unsure, the reference decides. Re-run the full suite after the fix, not just the repro.

### Source-level fixes that ripple
When a component hardcodes a value that should mirror a shared registry/config, fix it at the **source** (mirror the registry) so it stays in sync — but **grep the whole test tree for the symbol first**: hand-rolled tests and mocks reimplement the old shape and will fail on a shard you did not run. Update every assertion that encoded the old value, consistently.

## Phase 4: Golden / snapshot tests

Regenerate the golden, then **diff old-vs-new and confirm the delta is exactly the intended change** before accepting the new hash. A golden that changed for an unrelated reason is a regression, not a refresh — a byte-identical test that went red is a signal to inspect, not a hash to bump.

## Phase 5: Lock it

Turn the checker into a regression test at the **correct seam** (the real call site, not a shallow unit seam that can't replicate the chain). Watch it fail, confirm the fix makes it pass, and re-run the checker against the original un-minimised scenario.
