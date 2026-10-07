# Validating a comparison harness before trusting its verdict

When a finding rests on a harness you wrote, the harness is the instrument. A
defective instrument produces confident, well-formatted fiction — worse than no
answer, because it survives review on presentation.

## The control run

Before reporting anything a harness says about code under audit, run the
**known-good reference** through the *same* harness.

- The reference reproduces exactly → the harness is sound; its verdicts carry weight.
- The reference does not reproduce → **the harness is wrong.** Stop, fix it, discard
  every earlier finding from it.

This is the single highest-value check in the whole exercise. It is cheap (one run)
and it is the only thing that distinguishes "the code disagrees with ground truth"
from "my comparison is broken."

## Three defects that account for nearly all broken harnesses

### 1. Reimplemented the rule under test

Reading a function and writing your own equivalent of it in the harness is the
largest source of false findings. You will encode a rule the code does not have,
then report the gap as a defect with a citation.

**Instead:** call the real function, filter its output. If a post-filter is
unavoidable, justify it from the function's own docstring or source — not from
your memory of how it ought to work.

Corollary: when a function's rule is non-obvious (e.g. "skip only if *both*
bodies' thresholds are exceeded" is not the same as `min(a, b)`), read the
source before writing anything that reproduces it.

### 2. Synthetic inputs

A hand-picked angle, date, or separation chosen because it "should" trigger
nothing proves nothing. The function returning an empty set for an arbitrary
value is correct behaviour, not a bug.

**Instead:** drive real data from a real case. Sweep a real date range, use real
positions, compare against real ground truth. When a suspicious result appears,
re-run it at real values before escalating its severity.

### 3. Cross-layer identifiers

The same concept carries different identifiers in different layers — `conj`/`sq`/
`trine` in one library, `Conjunction`/`Square`/`Trine` in another; `Pluto` vs
`pluto`; degrees vs arcseconds.

**Symptom:** a set diff reporting dozens of mismatches that are all obviously the
same thing under different labels.

**Instead:** build an explicit normalisation map and apply it on both sides before
comparing. A diff full of near-identical entries differing only in casing or
spelling is an identifier bug, not a behavioural one.

## Severity honesty

A percentage divergence is not a severity claim on its own. Report the *direction*
of the error: aspects that should not be there (false positives) mean the rule is
too loose; missing ones mean too tight. That distinction changes what you fix.

Also state sample size and what the number covers. "Wrong on 3% of checks" drawn
from a sweep of one planet pair is not the same claim as one drawn from all pairs,
and quoting the former as general is how a real-but-marginal finding gets
overweighted.

## Ledger discipline

Keep a running record of each harness revision and what it ruled in or out. When a
later revision contradicts an earlier number, the contradiction is the signal —
it means the earlier harness was wrong, and every finding from it is suspect.

## Retraction

If a later check falsifies a finding you already reported, retract it in place and
loudly: name the finding, name the harness defect that produced it, and state what
survives. Do not quietly correct the report — a reader who saw the original
severity needs to know it was wrong, or they will act on it.