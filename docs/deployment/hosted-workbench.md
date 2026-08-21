# Hosted retained workbench deployment

## Purpose

The public Render service is a read-only deployment of the accepted Stage 4 retained sessions. It must
show the MOT17-02-DPM and KITTI Tracking 0000 package chains, retained WAV files, source frames and verified
Stage 3 metrics declared by `configs/workbench/retained-sessions.v0.1.0.json`.

The service does not regenerate research outputs and does not substitute synthetic events or metrics.

## Deployment boundary

Large retained packages and source media remain outside Git. A deterministic ZIP bundle is built locally
from the same roots used by the accepted local workbench and is supplied to Render through an external
HTTPS location.

The bundle builder validates both retained sessions before copying any files. Render then verifies the
complete archive SHA-256, validates the bundle manifest against the committed catalogue, and opens both
sessions through the unchanged Stage 4 validation path before serving HTTP requests.

## 1. Prepare local bindings

The existing `.env`/runtime values must identify:

```text
MOT17_ROOT=<root containing train/MOT17-02-DPM/img1>
KITTI_TRACKING_ROOT=<root containing training/image_02/0000>
STAGE2_EVIDENCE_ROOT=<retained evidence root containing mot17/run-a and kitti/run-a>
```

The values can be exported into the shell or supplied explicitly to the bundle command.

## 2. Review dataset redistribution conditions

Source frames are not project-generated artefacts. The applicable MOT17 and KITTI licence/terms must be
reviewed before placing a bundle containing those frames at a public URL. The builder requires an explicit
acknowledgement flag so this release decision cannot happen accidentally.

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

Upload the ZIP to a location that Render can download over HTTPS. Do not commit the bundle, dataset frames,
retained WAV files or machine-specific roots to this repository.

Preserve the generated SHA-256 separately from the archive URL.

## 5. Configure Render

The service requires:

```text
WORKBENCH_BUNDLE_URL=<https URL of event-sonification-retained-workbench.zip>
WORKBENCH_BUNDLE_SHA256=<64-character SHA-256 printed by the builder>
```

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
