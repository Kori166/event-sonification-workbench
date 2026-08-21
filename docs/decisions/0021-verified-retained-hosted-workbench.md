# 0021: Verified retained hosted workbench

## Status

Accepted, 21 August 2026.

## Context

Decision 0020 introduced a synthetic Render demonstration to avoid copying externally stored datasets and
retained generated packages into Git. The deployed service was technically functional but did not expose
the accepted Stage 4 retained sessions. It instead displayed a four-event synthetic sequence, generated
placeholder frames and no Stage 3 technical metrics.

The hosted artefact is intended to provide remote read-only inspection of the same bounded cases used by
the completed workbench: MOT17-02-DPM and KITTI Tracking sequence 0000. Their session declarations and
canonical Stage 3 evaluation reports are committed, while the required Stage 1/2 package directories,
retained WAV files and source frames remain outside Git.

## Decision

The Render service will load a researcher-built external deployment bundle rather than generating a
synthetic chain at startup.

- The accepted retained-session catalogue remains
  `configs/workbench/retained-sessions.v0.1.0.json`.
- The bundle contains only the package directories and source-frame trees required by those declared
  MOT17-02-DPM and KITTI Tracking 0000 sessions.
- Before a bundle is created, both retained sessions are opened through the existing Stage 4 validator.
  Package identities, file hashes, configuration identities, media bindings and Stage 3 report links must
  therefore match the committed session declarations.
- Bundle creation is deterministic: archive entries are ordered, timestamps are fixed and the complete ZIP
  archive receives a SHA-256 digest.
- Render receives the bundle through an external HTTPS location. The expected archive SHA-256 is supplied
  separately as deployment configuration.
- Startup fails closed if the bundle URL/path is absent, the SHA-256 is absent or mismatched, the archive is
  unsafe, the bundle manifest does not match the committed retained catalogue, media counts differ, or an
  accepted session fails the unchanged Stage 4 validation path.
- The public server may bind to `0.0.0.0` only through the existing explicit hosted-mode boundary. The local
  `inspect-session` command remains loopback-only by default.
- The previous `hosted_demo` module becomes a compatibility entry point to the retained hosted service so an
  existing Render start command cannot silently continue serving the synthetic sequence.
- Source media are not committed to Git. Bundle creation requires explicit researcher acknowledgement that
  the applicable dataset licence and redistribution terms have been reviewed before source frames are
  packaged for public hosting.

## Rationale

This approach keeps the public interface aligned with the completed artefact without changing the accepted
research evidence. The hosted service consumes the same retained event, cue, suppression, audio and Stage 3
identities already frozen by the session declarations. No new metrics are calculated and no synthetic values
are substituted for canonical findings.

Using an externally stored bundle avoids adding large generated packages or dataset media to the source
repository. Requiring an archive hash and re-running Stage 4 session validation makes deployment inputs
traceable and prevents a different or partially copied package from being presented as the retained case.

## Consequences

- The hosted service will not start until a valid retained deployment bundle is supplied.
- A local bundle must be created from the existing `STAGE2_EVIDENCE_ROOT`, `MOT17_ROOT` and
  `KITTI_TRACKING_ROOT` bindings and then placed at an HTTPS-accessible location suitable for Render.
- The bundle SHA-256 becomes part of the deployment record and must be preserved with the hosted release
  notes or project log.
- Dataset-media redistribution remains a researcher-controlled release decision and must be checked against
  the applicable terms before public deployment.
- The canonical dissertation findings remain the committed Stage 3 reports. Hosting does not create new
  evidence of accessibility, usability, navigation benefit, perceptual effectiveness or safety.
