# Milestone 2: MOT17 Vertical Slice

## 1. Context

This milestone reconstructs the MOT17 parser component in the rebuilt repository. Evidence from the
deleted repository and earlier dissertation claims was excluded. The work ends after normalised
event creation and validation.

## 2. Milestone objective

Create a fixed, reproducible MOT17 fixture mechanism and convert the selected evidence through the
first dataset parser into schema-valid common events.

## 3. Initial repository state

The local checkout began on legacy commit `583a73e7e4dc399ef1ad2d343366facd9896e750`.
`origin/main` identified the rebuilt repository at
`22891ccd81daf7ac79aeffea256d9e24d475d7e5`. The histories had no common ancestor. Two untracked
build directories were preserved in a named Git stash. Rebuilt `main` was inspected in detached
state rather than joined to the deleted history.

An existing remote milestone branch and draft pull request contained a partial adapter and
synthetic format tests. The branch head before this work was
`a613645ccd86664c72ef7fdf6a0ca802124ac3e2`.

The environment used Windows, Python 3.14.3, jsonschema 4.26.0, pytest 9.1.1 and Ruff 0.16.1.
GitHub CLI was not installed. The connected GitHub integration remained available for issue and
pull-request operations.

## 4. Initial test result

`python -m pytest` on rebuilt `origin/main` collected eight tests. Six passed and two failed. Both
failures reported that the synthetic source-file SHA-256 did not match the checked-out CSV. The
observed Windows hash differed from the committed LF-based hash.

## 5. Dataset discovery

`MOT17_ROOT` resolved to a directory containing `train` and `test`. The preferred ground-truth and
sequence-metadata files existed, were readable and were available offline. The annotation file
contained 30,003 physical rows. Observed evaluation marks were zero and one. Observed class
identifiers were 1, 2, 4, 7, 8 and 9. Observed visibility ranged from zero to one.

No offline-file read failure occurred. The reparse-point attribute alone was not treated as a
problem.

## 6. Sequence selected

`MOT17-02-DPM` was selected from the training split as requested. The sequence declares 30 frames
per second, 600 frames and images of 1920 by 1080 pixels. No fallback sequence was required.

## 7. Dataset documentation inspected

A recursive search under the local MOT17 root found no file named as a README, licence, terms,
format document or PDF. No dataset-relative terms file was therefore available to inspect.

The following input files were inspected:

- `MOT17/train/MOT17-02-DPM/gt/gt.txt`;
- `MOT17/train/MOT17-02-DPM/seqinfo.ini`.

Format and class definitions were checked against Milan et al., *MOT16: A Benchmark for
Multi-Object Tracking*, Tables 5 and 6, and the official MOTChallenge instructions. These sources
support the nine ground-truth columns, evaluation-mark treatment, class identifiers, visibility and
one-based source conventions. They do not supply a redistribution grant for the local annotations.

## 8. Licence and fixture decision

Redistribution permission remains unresolved. Public download availability was not treated as
permission. Copied dataset rows were not committed. A manifest-driven generator creates the real
12-row fixture under `.local-fixtures/`. A structurally equivalent 12-row synthetic fixture and
independently calculated golden projection support normal CI.

Issue #3 must remain open under the milestone brief. Milestone 2 cannot be marked fully complete.

## 9. Fixture selection procedure

The first 5,000 physical annotation lines were inspected. The earliest three-frame interval was
used. Four tracks were retained in source order to cover an unmarked static person, a marked
pedestrian, a partially visible marked pedestrian and a lower-visibility unmarked person on a
vehicle. Three consecutive observations were retained for every selected track.

Selected physical source lines are `1, 2, 3, 601, 602, 603, 3613, 3614, 3615, 4856, 4857, 4858`.
The source annotation SHA-256 is
`2e3ecb488da8886d3200d402b2b08890c6d2879923839444e9b74fa43a551440`. The generated fixture
SHA-256 is `a4d5ec744f02febec5a2887080cc95c2f49b09189fa600d2e37c3252210f835f`.

## 10. Implementation sequence

1. The existing branch and common schema were audited.
2. Local dataset readability, metadata, format values and documentation were inspected.
3. The licence boundary and deterministic source-line selection were recorded.
4. Native coordinate preservation, class support and parser diagnostics were corrected.
5. Manifest-driven private fixture generation was implemented.
6. Synthetic valid, invalid and golden fixtures were added.
7. Unit, fixture, determinism, validation and integration tests were added.
8. Full-sequence validation performance was corrected without reducing checks.
9. Technical, decision and project records were updated.

## 11. Problems encountered

Four actual problems occurred:

- the local `main` history did not share an ancestor with rebuilt `origin/main`;
- GitHub CLI was unavailable;
- Windows line-ending conversion invalidated a hashed fixture;
- the first full `mot17-check` exceeded 120 seconds.

Unresolved redistribution permission is a methodological limitation rather than an implementation
error. No offline-file placeholder problem occurred.

## 12. Diagnostic evidence

`git rev-list --left-right --count main...origin/main` reported 19 local-only and 20 remote-only
commits, while `git merge-base` returned no ancestor. `gh` was not recognised as a command.

The baseline expected source hash began `5e3257`, while the checked-out CRLF file hash began
`9f77b8`. The initial full check timed out after 124 seconds. Inspection showed that each event
recompiled the schema and re-read the same source file for hashing.

## 13. Attempted solutions

The deleted history was not merged or rewritten. Rebuilt `origin/main` was inspected detached, then
the existing milestone branch was tracked directly. GitHub operations were routed through the
connected integration where possible.

LF attributes were added for hashed fixture formats, and the affected CSV was normalised. The full
validation attempt was rerun after introducing a per-run compiled schema and source-hash cache.

## 14. Resolutions or workarounds

The branch remained based only on rebuilt `main`. The preserved build artefacts remain recoverable
from the named stash. Cross-platform fixture hashing now passes locally. Per-event source-hash
validation remains active, but the physical file is read once per validation run. The repeated full
check completed in 21.1 seconds.

GitHub CLI remains unavailable. This does not affect local Git push or connected issue, pull-request
and merge operations.

## 15. Decisions made

- Common frames are zero-based; native bounding-box coordinates are preserved.
- Timestamps use the converted frame divided by sequence frame rate.
- The evaluation mark remains metadata; common confidence is `null`.
- The authoritative class definition contains identifiers 1 to 12; unknown values are errors.
- Visibility is preserved without thresholding.
- Out-of-frame geometry is retained with a warning.
- Logical source paths begin `MOT17/` and exclude private roots.
- Dataset-derived fixture rows remain ignored while permission is unresolved.

## 16. Tests performed

The following commands were run during development:

- `python -m pip install -e ".[dev]"`;
- `python -m pytest`;
- `python -m pytest -m "not integration"`;
- `python -m pytest -m integration` with `MOT17_ROOT` configured;
- `python -m ruff check .`;
- `python -m compileall -q src`;
- `python -m event_sonification_workbench.cli mot17-fixture ...`;
- `python -m event_sonification_workbench.cli mot17-check --sequence MOT17-02-DPM`.

## 17. Test results

The normal suite passed with 45 tests and one integration test deselected. The integration selection
passed with one test and 45 tests deselected. The complete suite passed twice with 46 passed, zero
failed, zero skipped and no pytest warnings. Ruff and Python compilation passed.

## 18. Determinism evidence

Two conversions of the synthetic fixture produced identical source-row order, event order, event
identifiers, event dictionaries, canonical JSON bytes and canonical event hashes. The private
generator reproduced the manifest SHA-256. The source line selection is sorted and source ordered.

## 19. Integration evidence

The private integration test generated 12 rows with the declared fixture hash. The full source
parser produced 30,003 valid events, zero invalid rows and zero blank rows. All 12 selected events
passed schema, event-ID, timestamp, geometry, normalised geometry, source-existence, source-hash and
canonical-hash checks. The full command reported 988 out-of-frame warnings and zero invalid events.

## 20. Limitations

The selected rows are not statistically representative. No images are included or required. Normal
CI cannot access the private source. Redistribution permission remains unresolved. The schema has
not been reviewed against KITTI Tracking. Structured event-package writing is not implemented.

## 21. Unresolved questions

An explicit redistribution permission or an approved acceptance-criterion interpretation is needed
before Issue #3 can close. The final common class vocabulary and KITTI-specific quality-field
treatment remain open for Milestone 3.

## 22. Consequences for the KITTI milestone

The common schema remains version `0.1.0`. KITTI Tracking must be assessed independently. MOT17
class, visibility and evaluation-mark decisions must not be projected onto KITTI without evidence.

## 23. Final completion assessment

The parser, private fixture mechanism, synthetic golden fixture, integration evidence, provenance
and determinism requirements are implemented. Issue #2 closed after its acceptance evidence and CI
result were added. Issue #3 and Milestone 2 remain open because redistribution permission is
unresolved. Stage 1 and KITTI Tracking remain incomplete.

The staged-tree search for the four prohibited private path and username patterns returned no
matches. `.env`, `.local-fixtures/`, distribution output and generated package metadata were ignored
and absent from the staged file list. No image, video, audio or full dataset file was staged. A
search for the first real annotation row returned no repository match. The committed valid fixture
contains 12 synthetic rows, and the real selection remains manifest-only.
