# 0021: Verified Hosted Workbench

## Status

Accepted, 21 August 2026.

## Context

Decision 0020 introduced a synthetic hosted demonstration because the full datasets and generated evidence were stored outside Git.

Although the demonstration worked, it did not show the final retained MOT17 and KITTI sessions used by the completed workbench. Instead, it used a small synthetic example with placeholder frames and no Stage 3 evaluation results.

The hosted workbench should provide remote, read only access to the same two retained cases used in the final artefact:

* `MOT17-02-DPM`
* KITTI Tracking sequence `0000`

The session definitions and Stage 3 evaluation reports are stored in the repository. The larger event, cue, audio and source image files remain outside Git.

## Decision

The hosted workbench will use a verified external deployment bundle containing the retained evidence rather than creating synthetic data when the service starts.

The following rules apply:

* The retained session list remains `configs/workbench/retained-sessions.v0.1.0.json`.
* The bundle contains only the files required for the retained MOT17 and KITTI sessions.
* Both sessions must pass the existing Stage 4 validation before the bundle is created.
* Package identities, hashes, configurations, source media and Stage 3 reports must match the committed session definitions.
* Bundle files are created in a fixed order with fixed timestamps so the resulting ZIP is repeatable.
* The completed ZIP receives a SHA 256 hash.
* Render loads the bundle from an external HTTPS location.
* The expected bundle hash is supplied separately through deployment configuration.
* The hosted service must stop if the bundle or expected hash is missing or incorrect.
* The service must also stop if the archive is unsafe, files are missing or a retained session fails validation.
* Public hosting may use `0.0.0.0` only through the explicit hosted mode.
* The normal local inspection command remains limited to the local machine by default.
* The previous synthetic hosted entry point now redirects to the retained hosted service.
* Source dataset media remain outside Git.
* Dataset licence and redistribution terms must be checked before source images are included in a public deployment bundle.

## Rationale

This approach makes the hosted workbench match the completed local artefact.

It uses the same retained events, cues, suppressions, audio and Stage 3 results. It does not create replacement metrics or substitute synthetic results.

Keeping the deployment bundle outside Git also avoids adding large generated files and dataset media to the repository.

The bundle hash and existing Stage 4 validation provide checks that the hosted version is using the expected retained evidence rather than an incomplete or different copy.

## Consequences

* The hosted workbench will not start without a valid retained deployment bundle.
* The bundle must be created from the existing retained Stage 2 evidence and configured MOT17 and KITTI dataset locations.
* The bundle SHA 256 must be retained as part of the deployment record.
* Dataset media can only be publicly hosted after the relevant redistribution terms have been reviewed.
* Hosting does not change the Stage 3 evaluation results.
* The hosted workbench remains a read only inspection tool.
* Hosting does not provide evidence about accessibility, usability, navigation, perceptual effectiveness or safety.