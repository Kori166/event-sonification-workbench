# Milestone 2 fixture licence resolution

## Context

Issue #3 remained open after the MOT17 parser was completed because the local dataset copy did not
include a licence file. The dataset-derived fixture therefore remained outside Git while the
redistribution position was checked.

## Evidence reviewed

The official MOTChallenge website states that datasets provided on the site are published under the
Creative Commons Attribution-NonCommercial-ShareAlike 3.0 licence.

- MOTChallenge: https://motchallenge.net/
- Licence: https://creativecommons.org/licenses/by-nc-sa/3.0/

## Decision

The selected 12-row MOT17 annotation extract will be committed for non-commercial academic testing.
The extract will retain attribution and a reference to the applicable licence. Images and complete
annotation files will not be committed.

## Fixture evidence

- Sequence: `MOT17-02-DPM`.
- Source lines: `1, 2, 3, 601, 602, 603, 3613, 3614, 3615, 4856, 4857, 4858`.
- Source annotation SHA-256:
  `2e3ecb488da8886d3200d402b2b08890c6d2879923839444e9b74fa43a551440`.
- Fixture SHA-256:
  `a4d5ec744f02febec5a2887080cc95c2f49b09189fa600d2e37c3252210f835f`.
- Fixture: `tests/fixtures/mot17/dataset-derived/gt_fixture.txt`.
- Notice: `tests/fixtures/mot17/dataset-derived/NOTICE.md`.

The committed fixture matches the deterministic selection and hash recorded during the real-data
integration run.

## Consequences

Issue #3 can close once the change is merged and CI passes. Milestone 2 can then be marked complete.
The full MOT17 dataset remains local, and the full-sequence integration test still requires
`MOT17_ROOT`.

Milestone 3 will implement the KITTI Tracking fixture and parser.
