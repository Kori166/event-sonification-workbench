# 0020: Hosted demonstration deployment boundary

## Status

Superseded by Decision 0021 on 21 August 2026.

## Context

The Stage 4 inspection workbench was intentionally implemented as a loopback-only read service over
retained Stage 1-3 evidence. The complete local sessions depend on externally stored MOT17 and KITTI
Tracking media and retained generated packages that are deliberately excluded from Git. A Render web
service, by contrast, must bind to a public interface and cannot depend on the researcher's local dataset
or evidence paths.

Publishing the retained real-data tree would weaken the established storage, redistribution and evidence
boundaries. Making the normal inspection command publicly bindable by default would also weaken the
local security boundary merely to satisfy deployment infrastructure.

## Decision

A separate bounded hosted-demonstration path will be used.

- The existing inspection server remains loopback-only by default.
- Public wildcard binding is accepted only when a caller explicitly enables hosted binding, and only for
  `0.0.0.0` or `::`.
- The hosted entry point generates a small deterministic deployment chain from the committed synthetic
  Stage 2 fixture using the existing event-package, cue-scheduling and audio-rendering implementations.
- Four synthetic normalised events are used: two produce cues and two produce explicit suppressions under
  the frozen baseline preset.
- Synthetic PNG frames are generated at startup so that no MOT17 or KITTI source imagery is redistributed.
- The hosted sequence is named `synthetic_hosted_demo`. It uses the existing MOT17 session-contract branch
  only because Workbench Session Contract `0.1.0` admits the two implemented dataset families; the
  conversion notes explicitly state that the sequence is synthetic and is not a real MOT17 sequence.
- The generated package is validated through the unchanged Stage 4 session-opening path before the browser
  service is exposed.
- No Stage 3 technical-evaluation report is attached to the hosted synthetic session. The hosted interface
  therefore reports evaluation as unavailable rather than substituting synthetic values for the canonical
  dissertation evidence.
- Render deployment is declared in the repository through `render.yaml` and launches only the bounded
  hosted entry point.

## Rationale

This separated deployment convenience from research evidence, but the resulting public service did not
represent the retained workbench used for Stage 4 inspection. It exposed a four-event synthetic sequence,
synthetic images and no Stage 3 metrics. This made the deployment unsuitable as the intended hosted form
of the completed artefact.

The synthetic chain was built with the production package writer, scheduler, renderer and session
validator, so it remained useful as a development experiment. It is no longer the public deployment path.

## Consequences

- The synthetic hosted sequence must not be used as the public artefact demonstration.
- Decision 0021 replaces the synthetic deployment with a verified external bundle containing the accepted
  retained MOT17-02-DPM and KITTI Tracking 0000 inspection inputs.
- The loopback-only default for the local workbench remains unchanged.
