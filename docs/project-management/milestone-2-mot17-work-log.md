# Milestone 2 Work Log: MOT17 Vertical Slice

## Milestone objective

Create a fixed MOT17 fixture and convert it through the first dataset adapter into validated common
events.

## Work completed on 29 July 2026

- Added the MOT17 adapter under `src/event_sonification_workbench/adapters/`.
- Added explicit parsing for `seqinfo.ini` and the nine-column ground-truth format.
- Added deterministic frame, timestamp, coordinate, class and provenance conversion.
- Added a versioned MOT17 class mapping.
- Added a synthetic MOT17-format fixture for parser unit tests.
- Added controlled invalid rows for error-path tests.
- Added `mot17-check` for local parsing and validation without writing outputs.
- Added `mot17-fixture` for deterministic extraction of explicitly selected source rows.
- Extended common event validation so dataset-relative paths can be resolved from a configured
  source root rather than the repository root.
- Added adapter, validation, command-line and fixture-extraction tests.
- Recorded the format decisions in Decision 0007 and the adapter documentation.

## Difficulties and resolutions

### Dataset access

The connected repository environment does not have access to the local OneDrive dataset folders.
The implementation can therefore be tested against controlled format data, but a real MOT17
fixture cannot be selected or verified in this environment without the source files.

**Resolution:** parser implementation and controlled tests were completed first. The real-data
quality gate remains explicit rather than being replaced by synthetic evidence. The selected
sequence `seqinfo.ini` and `gt/gt.txt` are required to complete the milestone.

### Ambiguous `conf` terminology

MOTChallenge format descriptions use the name `conf` for the seventh column. In ground-truth
files, this value is an evaluation inclusion mark rather than detector confidence. Treating it as
confidence would support superficially plausible but incorrect filtering.

**Resolution:** common `confidence` is set to `null`. The source mark is retained in metadata and
its interpretation is recorded in Decision 0007.

### Ground truth and tracker-result field counts

MOT17 ground truth contains nine fields, while tracker-result files commonly contain ten. A parser
that accepted both without an explicit mode could shift column meanings silently.

**Resolution:** the ground-truth adapter requires exactly nine fields and reports a clear row error
for any other count.

### Indexing conventions

MOT17 frames and bounding-box origins are one-based, while the common schema uses zero-based
frames and coordinates.

**Resolution:** both conversions are explicit, covered by tests and recorded in each event's
conversion notes. Native values remain in metadata.

### Fixture provenance and redistribution

A dataset-derived fixture must be small, documented and permissible to commit. Selecting rows
without inspecting the local source would create weak or fabricated provenance.

**Resolution:** a deterministic extraction command now records selected physical row numbers,
source hashes and fixture hashes. Final row selection remains pending source inspection.

### Continuous-integration lint failure

The first pull-request CI run failed before the test stage. Ruff required abstract collection types to
be imported from `collections.abc` and required two import blocks to be reordered.

**Resolution:** the imports were corrected without changing parser behaviour. The subsequent CI
run passed lint and the complete automated suite.

## Validation evidence

The complete local test suite passed after the implementation was combined with the Milestone 1
tests:

```text
20 passed
```

Python compilation passed. No Python source or test line exceeded the configured 100-character
limit.

GitHub Actions CI run 25 completed successfully after the Ruff corrections. This confirms the
configured lint and automated test workflow on the milestone branch.

The tests cover synthetic and controlled inputs only. They do not provide evidence of a successful
run against the local MOT17 dataset.

## Remaining milestone actions

- Inspect `MOT17-02-DPM/seqinfo.ini` and `MOT17-02-DPM/gt/gt.txt` from the local dataset copy.
- Select a small set of representative physical rows and record the selection rationale.
- Generate and review the dataset-derived fixture and manifest.
- Run `mot17-check` against the selected real sequence.
- Add expected normalised events for the fixed fixture.
- Close Issues #2 and #3 only when their acceptance criteria are supported by real-data evidence.

## Evidence boundary

The parser implementation is ready for real-data verification. Milestone 2 is not complete until the
real fixture and local dataset run are recorded. This distinction prevents controlled format tests
from being reported as dataset compatibility evidence.
