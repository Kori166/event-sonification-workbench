# Stage 3 Milestone 1 Close-out

## Scope and base verification

The milestone defines technical-evaluation method `0.1.0` and verifies it using synthetic records
only. Before Stage 3 work, remote state was fetched and PR #23 (`Complete Stage 2 close-out`) was
confirmed merged into `main` at merge commit `2eab48b620fa11c50ecc6bbef1bd1356ac6c5995` on 6 August
2026. The Stage 2 checklist, project plan and close-out were present on that base.

The original local checkout contained unrelated interface work. It was preserved separately and a
clean worktree/branch `stage-3-evaluation-contract` was created from the merged base, so no Stage 2
close-out or interface changes were mixed into this milestone.

## Repository inspection and ambiguities

The project already supplied canonical compact JSON, SHA-256 helpers, stable diagnostic patterns,
JSON Schema validation, decimal half-up sample placement, half-open render ends, deterministic
event/cue ordering and exact package comparison. The evaluator reuses them. No parallel hashing or
serialisation framework and no dependency were added.

Inspection found these method ambiguities and resolved them in Decision 0013:

- Stage 2 emits one cue or suppression per event, but the evaluation definition allows future
  multiple cues. Distinct cues for one event count as one represented outcome; cue plus suppression
  is an error.
- A valid Stage 2 input event with no outcome is eligible and missed because every intentional
  suppression must be explicit.
- Correct half-up rendering can have zero integer placement error and a non-zero seconds-domain
  quantisation difference; both are retained.
- Rendered duration, including trailing silence, is the preferred density/overlap denominator.
- Equal interval boundaries are grouped as half-open boundaries, preventing instantaneous false
  overlap peaks.
- Missing repeat evidence is null, and successful execution never implies reproducibility.

The minimum Milestone 1 CLI consumes a prepared validated record-chain document. Extracting and
verifying selected real package chains for dataset-level reports remains Milestone 2 work.

## Contract and evaluator

The normative machine policy and its schema are:

- `configs/evaluation/technical-evaluation-contract.v0.1.0.json`;
- `configs/evaluation/technical-evaluation-contract.schema.v0.1.0.json`; and
- `configs/evaluation/technical-evaluation-report.schema.v0.1.0.json`.

The human method is `docs/evaluation/technical-evaluation-contract-v0.1.0.md`. The evaluator records
contract/event/cue/renderer/preset/mapper versions; event, preset, schedule, suppression, render,
WAV, renderer, cue-package and audio-package hashes; dataset/sequence; timeline; every metric
numerator/denominator; deterministic diagnostics; run ID; and a non-recursive report payload hash.
Final exact-byte SHA-256 is returned by the canonical writer.

Stable hard failures cover unsupported versions and malformed records. An evaluable miss is a
warning; duplicate IDs/outcomes, orphan references, provenance disagreement and repeat mismatches
are errors. Errors make a report invalid. Supplied events are not modified or reordered.

## Manual oracle

The project-authored fixture contains five source events on a 10 Hz, three-second rendered
timeline. Four events are eligible and represented by five cues, including two cues for one event;
one event is intentionally suppressed. Cue intervals include exact boundaries, touching intervals,
overlaps and a 2.25-second start that rounds half-up to sample 23.

Manual expected headline values are:

- eligible coverage `4/4 = 1`, source representation `4/5 = 0.8`, suppression `1/5 = 0.2`,
  accounting `5/5 = 1`, missed `0/4 = 0`;
- scheduling seconds: count 5, min 0, max 0.5, mean 0.1, median 0, p95 0.5;
- render-placement seconds: count 5, min 0, max 0.05, mean 0.01, median 0, p95 0.05, while all
  integer placement errors are zero;
- end-to-end seconds: count 5, min 0, max 0.5, mean 0.11, median 0, p95 0.5;
- 5/3 cues/s, 100 cues/min, 4/3 represented events/s and maximum two starts in `[t,t+1)`;
- peak concurrency 2, overlap 1.2 seconds, overlap proportion 0.4, excess 1.2 cue-seconds and
  normalised burden 0.4; and
- complete cue/suppression traceability with all four supplied repeat levels equal.

The full independently reviewed calculation and sweep segments are in
`tests/fixtures/evaluation_oracle/oracle-calculation.md`. Named negative cases inject an eligible
miss, orphan cue, unknown suppression, contradictory outcome, broken annotation link, one-sample
displacement and malformed values. Empty and non-empty zero-duration cases are constructed in
tests.

## Deterministic report evidence

- evaluation run ID: `evaluation-synthetic-evaluation_oracle-e1ee06d3a671ee1b`;
- report payload SHA-256: `302b97643f1f39b4adee63c9e78bc053640b8d6c4d56f818ad1e6896bb82cb21`;
- final canonical report SHA-256:
  `b5bcf1fc39987dfd7b61475e67d075312bd060f6dfb8adf2fa3f8300badaf908`; and
- committed golden-file physical SHA-256 (includes its fixture newline):
  `1ce3f1fb5472358001c86ffaf3859d7dfbbb22a156f0ceb94207d45bd2b430f4`.

Two evaluations from independent input copies produced identical documents, canonical bytes and
hashes. Two separately written files and the CLI output were also byte-identical.

## Tests and quality checks

Actual commands/results on Windows 10.0.26200, AMD64, Python 3.14.3:

- `python -m ruff check .`: passed.
- `python -m pytest tests/test_technical_evaluation.py -q`: 25 passed.
- `python -m pytest -m "not integration"`: 209 passed, 2 deselected.
- `python -m pytest -m integration`: 2 skipped, 209 deselected because both private root variables
  were unavailable. These skips are not integration-pass evidence.
- `python -m pytest`: 209 passed, 2 skipped for the same unavailable roots.
- `python -m ruff format --check` for the three changed Python files: passed after formatting.

CI config has no formatter or static type-check job and the development dependencies contain no
`mypy` or `pyright`. An additional whole-repository current-Ruff formatter check reported 14
pre-existing Python files that would be reformatted; no broad unrelated reformat was introduced.
The configured repository gates are Ruff lint and non-integration pytest, and both pass.

## Limitations and next milestone

No full MOT17 or KITTI technical evaluation was run. No real coverage, alignment, traceability,
density or overlap result is claimed, and RQ3 remains incomplete. The synthetic repeat test is
same-process evidence; Stage 2 byte evidence remains bounded to its recorded Windows environment,
and cross-environment identity is untested. The metric contract supports no conclusion about
perception, participants, accessibility, usability, navigation or safety.

The exact next milestone is **Stage 3 Milestone 2: run the frozen technical-evaluation contract
against selected real MOT17 and KITTI Tracking evidence packages and produce deterministic
dataset-level evaluation reports.**
