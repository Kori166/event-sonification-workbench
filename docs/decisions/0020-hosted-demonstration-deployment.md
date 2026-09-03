# 0020: Hosted Demonstration Deployment

## Status

Superseded by Decision 0021 on 21 August 2026.

## Context

The Stage 4 workbench was designed as a local read onlly inspection tool over retained Stage 1 to 3 evidence.

The full MOT17 and KITTI sessions depend on dataset media and generated evidence stored outside Git.

A public Render service cannot use the researcher's local paths, and publishing the full retained data would weaken the existing storage and redistribution boundaries.

The local inspection server also should not be made publicly accessible by default just to support hosting.

## Decision

A separate hosted demonstration was created using synthetic data.

The following rules applied:

* The normal inspection server remained local only by default.
* Public binding was allowed only when hosted mode was explicitly enabled.
* The hosted demonstration generated a small deterministic example using the existing event, cue and audio pipeline.
* Four synthetic events were used.
* Two events produced cues.
* Two events produced explicit suppressions.
* Synthetic PNG frames were generated so no MOT17 or KITTI source images were redistributed.
* The hosted sequence was named `synthetic_hosted_demo`.
* The sequence used the existing session validation path.
* The documentation clearly stated that it was synthetic and not a real MOT17 sequence.
* The generated package had to pass the normal Stage 4 sesion validation before being displayed.
* No Stage 3 evaluation report was attached.
* The interface therefore showed evaluation results as unavailable rather than inventing replacement values.
* Render deployment was defined through `render.yaml` and used only this bounded hosted entry point.

## Rationale

This approach provided a safe way to test public deployment without exposing private dataset paths or retained research data.

It also reused the package writer, cue scheduler, renderer and session validator, so the demonstration remained technically useful during development.

However, the hosted version did not represent the completed artefact.

It showed only a four event synthetic example, synthetic images and no Stage 3 technical results.

For that reason, it was later replaced by Decision 0021, which uses verified retained MOT17 and KITTI evidence.

## Consequences

* The synthetic hosted sequence is no longer used as the public artfact demonstration.
* Decision 0021 replaces it with a verified external bundle containing the retained MOT17 and KITTI sessions.
* The local workbench remains restricted to loopback access by default.
* The synthetic deployment remains part of the development history but is not part of the final research evidence.