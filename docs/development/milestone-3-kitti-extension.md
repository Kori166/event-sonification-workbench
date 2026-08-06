# Milestone 3: KITTI Tracking Extension

## Objective

Implement Issue #5 by inspecting the private KITTI Tracking copy, creating a deterministic and
licensed small fixture, converting annotations into the shared event interface, and validating a
complete training sequence. Sonification, audio generation and technical evaluation remain out of
scope.

## Repository and branch state

The requested branch `stage-1/milestone-3-kitti-extension` was created from `origin/main`, whose
tree matched the completed Milestone 2 branch. Pre-existing uncommitted interface work in
`.gitignore`, `README.md`, `Open Workbench.cmd` and `web/` was preserved. Milestone changes will be
staged explicitly so that unrelated files do not enter the pull request.

GitHub CLI was not installed. Local implementation and validation were not blocked; pull-request
creation requires the connected GitHub capability or later CLI availability.

## Dataset audit before implementation

The path was obtained from `KITTI_TRACKING_ROOT` through the ignored local environment
configuration. No absolute value was recorded.

The root contained `training` and `testing`. The discovered training annotation directory was
`training/label_02`, with 21 files named `0000.txt` through `0020.txt`. The same root also contained
training calibration, left-camera image, OXTS, pose and Velodyne directories. The test split had 29
corresponding sensor sequences but no ground-truth label directory.

All 21 training annotation files used 17 whitespace-separated fields. Observed native classes
across the local copy were `Car`, `Van`, `Truck`, `Pedestrian`, `Person`, `Cyclist`, `Tram`, `Misc`
and `DontCare`. `Person_sitting` did not appear literally; official TrackEval identifies `Person`
as the sitting-person distractor class.

No recursively searched file had a name suggesting licence, license, terms, README or copyright.
Official KITTI copyright/licence information was therefore used and the missing local terms file
was recorded explicitly.

## Official definition review

The official tracking benchmark page, official devkit format mirrored in TrackEval, official
TrackEval KITTI implementation, sensor setup and KITTI copyright page were reviewed. They establish:

- 21 training and 29 testing tracking sequences;
- zero-based time steps and 2D coordinates;
- sequence-unique track identifiers;
- eight object classes, local `Person` alias and `DontCare`;
- tracking-specific integer truncation 0–2;
- occlusion values 0 fully visible, 1 partly, 2 largely and 3 unknown;
- alpha observation angle and camera-Y rotation in `[-pi, pi]`;
- left/top/right/bottom 2D boxes;
- height/width/length and camera-coordinate x/y/z 3D geometry;
- an optional eighteenth result score with a dataset-determined range; and
- the evaluation role of `DontCare` regions.

## Fixture selection and integrity

Sequence `0000` was selected because it contains five native classes, all truncation levels, all
occlusion levels and `DontCare` while remaining the smallest early-sequence audit target. It has
1,089 rows over frames 0–153, 154 images at 1242 by 375 and an annotation SHA-256 of
`97f772a27181dfc7ef51b3e64b86bd42e682753b6855fdc58d259ecbed501fd4`.

The deterministic algorithm takes the first row for each class and the first row for each distinct
truncation/occlusion pair, then sorts and deduplicates the union. It selected source lines
`1, 3, 4, 5, 25, 31, 48, 52, 286, 310, 601, 629`. LF-normalised fixture SHA-256 is
`fe67e4e689ff4431464bf4ee040e79454bb2e9f0e9dd0331a594b9e6a3aab1b7`.

The fixture contains only those 12 rows. Its manifest, README and licence notice provide source
lines, field structure, method, hashes, attribution, CVPR 2012 citation and CC BY-NC-SA 3.0 terms.
Synthetic malformed rows are clearly separated.

## Parser and schema decisions

The parser converts all 17 required fields and the optional score through explicit types. It
preserves zero-based frames, track IDs, native/common classes, 2D geometry, truncation, occlusion,
alpha, 3D geometry, rotation, score and source provenance. Invalid rows produce coded structured
issues.

`DontCare` is preserved as `dont_care` with track `-1`, its box and placeholder values, and an
explicit metadata flag. It is not discarded or treated as a normal object silently.

Schema 0.1.0 was structurally sufficient but constrained confidence to `[0,1]`. Official KITTI
scores need not be normalised. Schema 0.2.0 therefore retains the exact shape and relaxes only that
constraint. MOT17 remains compatible and now emits 0.2.0 with confidence `null`.

## Tests and final local evidence

Automated coverage includes valid/invalid rows, explicit types, class aliases, frame/time, bounding
box conversion, truncation, occlusion, 3D fields, `DontCare`, optional score presence/absence,
scores outside `[0,1]`, deterministic IDs/hashes, fixture provenance, repeated conversion,
environment/layout errors and real-data integration.

The final private sequence `0000` run on 5 August 2026 recorded:

- 1,089 physical rows;
- 1,089 valid events;
- 378 preserved `DontCare` events;
- 0 confidence-bearing training rows;
- 0 errors; and
- 0 warnings.

All 1,089 events passed common schema and semantic/provenance validation. The fixture reproduced the
selected private source lines byte-for-byte after line-ending normalisation.

Before documentation, Ruff passed and the final non-integration suite reported 76 passed with two
integration tests deselected. The dedicated KITTI integration test reported one passed. Final
whole-repository command results are recorded in the progress log after completion.

## Problems and resolutions

- The process environment initially lacked the root while the ignored local environment file
  contained it. Commands exported the value only for the private integration process; no path was
  printed into committed records.
- PowerShell's runtime lacked `Path.GetRelativePath`; the audit used root-prefix-safe relative
  formatting instead.
- A first boundary rule warned on nine boxes ending exactly at image width/height. The converted
  representation treats right/bottom as continuous edges, so equality is valid. The final parser
  warns only outside `[0, width]` and `[0, height]` while preserving geometry.
- GitHub CLI was unavailable. This remains a publication tooling concern, not a parser defect.

## Acceptance assessment

Issue #5's parser criteria were implemented locally: conversion is explicit; required source values
and confidence are preserved; assumptions and `DontCare` are documented; failures are clear and
structured; and automated parser/integration tests pass. PR #15 subsequently passed CI and merged
on 5 August 2026, closing the milestone.
