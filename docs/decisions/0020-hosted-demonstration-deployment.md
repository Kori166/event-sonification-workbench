# 0020: Hosted demonstration deployment boundary

## Status

Accepted, 21 August 2026.

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

This separates deployment convenience from research evidence. The public demonstration can show the
inspection architecture, cue/suppression behaviour, audio playback and provenance interaction without
requiring private machine paths, large retained packages or externally obtained dataset media. At the same
time, the original local command and the retained real-data evidence chain remain unchanged.

The synthetic chain is built with the production package writer, scheduler, renderer and session validator
rather than with a second simplified mock implementation. This keeps the demonstration technically close
to the released workbench while preventing it from being mistaken for an additional evaluated case study.

## Consequences

- The public deployment is supplementary demonstration evidence, not the basis of the dissertation
  findings.
- MOT17-02-DPM and KITTI Tracking 0000 remain the bounded real technical evaluation cases.
- No participant, accessibility, usability, navigation, perceptual-effectiveness or safety evidence is
  introduced by hosting the interface.
- The local `inspect-session` workflow continues to reject public wildcard binding unless a separate
  hosted caller opts into the restricted public-bind mode.
- Deployment can be reproduced from the repository without copying local `.env` values, dataset roots or
  retained Stage 1-3 package roots to Render.
- The final public URL can be inserted into the README only after the Render service has been created and
  verified.
