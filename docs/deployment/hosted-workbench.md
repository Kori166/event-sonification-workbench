# Hosted retained workbench deployment

## Purpose

The public Render service is a read-only deployment of the accepted Stage 4 retained sessions. It must
show the MOT17-02-DPM and KITTI Tracking 0000 package chains, retained WAV files, source frames and verified
Stage 3 metrics declared by `configs/workbench/retained-sessions.v0.1.0.json`.

The service does not regenerate research outputs and does not substitute synthetic events or metrics.
It exists only to make the non-commercial MSc research artefact easier for a marker to inspect. The
bundle is deliberately limited to MOT17-02-DPM and KITTI Tracking sequence 0000; it is not a replacement
distribution of either complete dataset.

## Deployment boundary

Large retained packages and source media remain outside Git. A deterministic ZIP bundle is built locally
from the same roots used by the accepted local workbench and is supplied to Render through an external
HTTPS location.

The bundle builder validates both retained sessions before copying any files. Render then verifies the
complete archive SHA-256, validates the bundle manifest against the committed catalogue, and opens both
sessions through the unchanged Stage 4 validation path before serving HTTP requests.

Every bundle also contains `THIRD_PARTY_DATASET_ATTRIBUTION.txt`. Its fixed UTF-8 bytes and SHA-256 are
recorded in the bundle manifest, so startup rejects a release in which the notice is absent or modified.

## 1. Prepare local bindings

The existing `.env`/runtime values must identify:

```text
MOT17_ROOT=<root containing train/MOT17-02-DPM/img1>
KITTI_TRACKING_ROOT=<root containing training/image_02/0000>
STAGE2_EVIDENCE_ROOT=<retained evidence root containing mot17/run-a and kitti/run-a>
```

The values can be exported into the shell or supplied explicitly to the bundle command.

## 2. Review dataset redistribution conditions

Source frames are not project-generated artefacts. The local research copies were obtained from publicly
accessible Kaggle mirrors:

- KITTI Tracking: <https://www.kaggle.com/datasets/leducnhuan/kitti-tracking/data>
- MOT17: <https://www.kaggle.com/datasets/wenhoujinjust/mot-17>

Kaggle is recorded only as the acquisition route. Dataset identity, ownership, attribution and licensing
remain associated with the original [MOTChallenge](https://motchallenge.net/) and [KITTI Vision Benchmark
Suite](https://www.cvlibs.net/datasets/kitti/) projects, not the mirror uploaders.

The applicable original-project licence/terms must be reviewed before placing a bundle containing source
frames at a public URL. The builder requires `--acknowledge-media-redistribution` so this researcher-owned
release decision cannot happen accidentally. The flag records explicit acknowledgement that the terms were
reviewed; it is not an automated legal determination that publication or redistribution is permitted.

The embedded notice attributes both original projects, records the bounded sequences and frame counts,
identifies the project-recorded CC BY-NC-SA 3.0 terms and citations, and explains the non-commercial
academic inspection scope. No ownership of the original imagery is claimed.

## 3. Build the deterministic bundle

With the three roots exported as environment variables:

```bash
python scripts/build_hosted_workbench_bundle.py \
  --acknowledge-media-redistribution
```

Alternatively, supply the roots explicitly:

```bash
python scripts/build_hosted_workbench_bundle.py \
  --stage2-evidence-root <path> \
  --mot17-root <path> \
  --kitti-root <path> \
  --acknowledge-media-redistribution
```

The default outputs are:

```text
dist/event-sonification-retained-workbench.zip
dist/event-sonification-retained-workbench.zip.sha256
```

The ZIP is deterministic for the same validated input bytes. The command prints the archive SHA-256 and
the two retained session identifiers.

## 4. Place the bundle at an HTTPS location

Upload the ZIP and its `.sha256` companion to a stable location that Render can download over HTTPS. A
public GitHub Release asset is suitable when it provides a direct download without authentication. Do not
commit the bundle, dataset frames, retained WAV files or machine-specific roots to this repository.

Before configuring Render, download the public ZIP while logged out, recompute its SHA-256 independently,
and confirm that it matches the locally verified digest. Preserve that digest separately from the archive
URL.

## 5. Configure Render

The service requires:

```text
WORKBENCH_BUNDLE_URL=<https URL of event-sonification-retained-workbench.zip>
WORKBENCH_BUNDLE_SHA256=<64-character SHA-256 printed by the builder>
```

Clear the Render build cache when replacing an earlier bundle configuration, redeploy `main`, and do not
record a public workbench URL until both retained sessions have passed the checks below.

The repository `render.yaml` launches:

```bash
python -m event_sonification_workbench.workbench.hosted_retained \
  --host 0.0.0.0 \
  --port $PORT
```

An existing manually configured Render service should use the same start command and environment values.
The previous `hosted_demo` command is retained only as a compatibility alias and now delegates to the same
retained hosted service.

## 6. Verify the deployed service

A valid deployment must show both catalogue entries:

```text
MOT17 · mot17-02-dpm
KITTI Tracking · 0000
```

For each session, verify that:

- source frames are the expected sequence frames rather than generated placeholders;
- audio duration corresponds to the retained Stage 2 WAV;
- EVENT, CUE and SUPPRESS timeline records are populated from the retained packages;
- cue selection exposes the accepted provenance chain;
- the Technical Metrics panel is available and matches the verified Stage 3 report; and
- switching between MOT17 and KITTI changes all session-scoped evidence consistently.

The deployment must be treated as failed if the service reports `synthetic_hosted_demo`, if Stage 3 metrics
are unavailable for either retained session, or if startup reports a `hosted_bundle_*` error.

## Reproducibility record

The final release record should retain the deployment bundle SHA-256, repository commit, Render service URL
and the date of the verification above. The bundle itself is deployment material, not new experimental
evidence.
