# Synthetic MOT17-format fixture

## Purpose

This fixture tests the MOT17 adapter before a dataset-derived fixture is added. It follows the
nine-column MOT17 ground-truth structure and the standard sequence directory layout.

The values are synthetic. No MOT17 annotation rows or images are included. The fixture therefore
does not complete Issue #3, which requires a documented sample derived from a selected MOT17
sequence.

## Contents

- `MOT17-FORMAT-TEST/seqinfo.ini`: controlled sequence metadata.
- `MOT17-FORMAT-TEST/gt/gt.txt`: five structurally valid rows.
- `MOT17-FORMAT-TEST/gt/invalid_gt.txt`: four controlled invalid rows.

The valid rows exercise:

- one-based frame and bounding-box origins;
- repeated track observations;
- marked and unmarked ground-truth rows;
- pedestrian, static-person, distractor and car classes;
- decimal geometry;
- an out-of-frame box that produces a validation warning; and
- deterministic source-row traceability.

The invalid rows exercise negative box dimensions, invalid visibility, an unknown class identifier
and an incorrect field count.

## Evidence boundary

Passing these tests demonstrates parser mechanics, conversion rules and common-schema validation.
It does not demonstrate compatibility with a real MOT17 release or selected sequence. That evidence
requires `seqinfo.ini` and `gt/gt.txt` from the local dataset copy.
