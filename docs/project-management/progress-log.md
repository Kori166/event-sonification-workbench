# Progress Log

This document records the main progress of the project against the planned project timeline.

It summarises important work, decisions, problems, corrections and testing. More detailed technical evidence is retained in the relevant stage checklists, decision records, evaluation documents, GitHub Issues and pull requests.

Some project stages overlap because research, development, evaluation and reporting continued alongside each other.

## Current Project Status

| Stage | Status |
|---|---|
| Research Planning And Literature Review | Complete |
| Stage 0: Project Setup | Complete |
| Stage 1: Data Ingestion And Normalisation | Complete |
| Stage 2: Audio Cue Generation | Complete |
| Stage 3: Technical Evaluation | Complete |
| Stage 4: Workbench Development | Complete |
| Stage 5: Report And Submission Preparation | In Progress |
| Viva Preparation | In Progress |

## 7 April To 29 June 2026: Define The Project

### Work Completed

* Defined the project area around event based sonification of annotated video datasets.
* Refined the project aim, objectives and research questions.
* Established MOT17 and KITTI Tracking as the two main dataset cases.
* Defined the project as technical research infrastructure rather than a validated assistive technology.
* Established reproducibility, traceability and deterministic processing as core requirements.
* Reviewed the project scope with the supervisor.

### Main Decisions

* The project will focus on annotated tracking datasets rather than live video.
* MOT17 and KITTI Tracking will provide two different annotation formats for testing the common workflow.
* The project will evaluate technical behaviour rather than participant outcomes.
* Accessibility, usability, navigation and safety claims will remain outside the evidence unless participant research is carried out.
* Three research questions will cover data normalisation, deterministic sonification and technical evaluation.

### Outcome

The aim, objectives, research questions and project scope were sufficiently defined to support implementation.

## 7 April To 31 July 2026: Literature Review And Research Gap

### Work Completed

* Reviewed literature on sonification, auditory display and event based audio representation.
* Reviewed work on visual to auditory mappings.
* Reviewed reproducibility and provenance in data processing systems.
* Reviewed MOTChallenge and KITTI Tracking documentation.
* Compared existing work with the proposed workbench.
* Identified a gap around reproducible and traceable conversion of annotated video events into deterministic audio outputs.
* Continued literature review alongside early technical development.

### Main Decisions

* The workbench should not be presented as proving that the generated audio is useful to listeners.
* Mapping choices should be explicit, deterministic and traceable.
* Technical evaluation should measure properties such as coverage, timing, traceability, density, overlap and repeatability.
* Dataset differences should be described rather than treated as controlled experimental differences.

### Outcome

The literature review established the research context and supported the final project scope and evaluation design.

## 1 June To 28 June 2026: Stage 0 Project Setup

### Work Completed

* Created the `event-sonification-workbench` repository.
* Added the README and Python project structure.
* Added environment configuration and Git ignore rules.
* Added the command line entry point and initial smoke test.
* Added the project plan, progress log, risk register and supervision log.
* Created the initial GitHub Issues.
* Established CI and automated testing.
* Added early decision records covering project scope, dataset storage and implementation structure.

### Main Decisions

* GitHub Issues, commits and project records will provide evidence of project management.
* Full MOT17 and KITTI datasets will remain outside Git.
* Only small fixtures may be committed where licensing allows.
* The Python package will remain under `src/event_sonification_workbench/`.
* Development will move from common data representation to dataset adapters, sonification, evaluation and finally the inspection workbench.

### Problems And Corrections

The initial CI check failed because the smoke test file did not contain a runnable test.

A valid package import test and the required package files were added.

The earlier loss of the original repository also reduced the available implementation time. This was recorded as a project risk.

### Outcome

The repository, development structure and basic project management evidence were established.

Stage 0 was complete.

## 15 June To 5 August 2026: Stage 1 Data Ingestion And Normalisation

Stage 1 developed the common event representation and converted MOT17 and KITTI Tracking annotations into that format.

### Common Event Schema

* Added provisional common event schema `0.1.0`.
* Added a synthetic annotation and manually calculated expected event.
* Added deterministic event IDs and canonical hashing.
* Added event validation.
* Tested source traceability and deterministic conversion.
* Reviewed the schema against both real datasets.
* Updated the common event schema to `0.2.0`.

### Main Schema Decisions

* Common frame numbers use zero based indexing.
* Timestamps are calculated from frame number and frame rate.
* Native and common object classes are stored separately.
* Source annotation information is preserved.
* Geometry outside the image may be retained where it exists in the source data but is reported appropriately.

### MOT17 Support

* Implemented the MOT17 annotation adapter.
* Added sequence metadata parsing.
* Added the MOT17 class mapping.
* Added the `mot17-check` command.
* Added valid, invalid and synthetic fixture tests.
* Inspected all 30,003 rows of `MOT17-02-DPM`.
* Added deterministic source row selection and fixture generation.
* Preserved native bounding box coordinates.
* Converted one based source frames to zero based common frames.
* Preserved the MOT17 evaluation mark as metadata rather than treating it as confidence.

### MOT17 Verification

The selected sequence produced:

* 30,003 valid events
* 0 invalid events
* 988 permitted geometry warnings

Repeated conversion produced the same event order, IDs, JSON and hashes.

### KITTI Tracking Support

* Inspected the KITTI Tracking annotation structure.
* Confirmed the local dataset contained 21 annotation sequences.
* Reviewed the official annotation format and licence information.
* Implemented KITTI parsing with explicit type conversion.
* Preserved frames, tracks, classes, truncation, occlusion, alpha, 2D and 3D geometry, rotation and optional scores.
* Preserved `DontCare` records as explicit events.
* Added deterministic KITTI fixtures and malformed test cases.

### KITTI Verification

KITTI Tracking sequence `0000` produced:

* 1,089 valid events
* 378 `DontCare` events
* 0 errors
* 0 final warnings

Repeated fixture conversion produced identical event records, IDs and hashes.

### Collection Validation

* Added validation for complete event collections.
* Added duplicate ID detection.
* Added stable error and warning codes.
* Added deterministic validation reports and hashes.
* Confirmed validation does not modify or reorder supplied events.

### Event And Provenance Outputs

* Added deterministic event package generation.
* Produced `events.json`.
* Produced `events.csv`.
* Produced `run_metadata.json`.
* Produced `provenance_log.json`.
* Added deterministic run IDs.
* Recorded source, configuration and output hashes.
* Added MOT17 and KITTI package commands.

### Repeatability

For both datasets, repeated package runs produced:

* the same run IDs
* the same event order
* identical JSON
* identical CSV
* identical metadata
* identical provenance records
* identical SHA 256 values

### Stage 1 Verification

* Ruff passed.
* 121 tests excluding integrations passed.
* Both private dataset integrations passed.
* All 123 configured tests passed.

### Outcome

Both selected datasets could be converted into validated common schema `0.2.0` event packages with retained provenance.

Stage 1 was complete.

## 29 July To 6 August 2026: Stage 2 Audio Cue Generation

Stage 2 converted validated events into deterministic audio cues and rendered WAV output.

### Cue Generation

* Added sonification preset schema `0.1.0`.
* Added baseline preset `0.1.0`.
* Defined mapping rules, parameter limits and suppression rules.
* Added deterministic cue IDs.
* Added cue and suppression records.
* Added the `schedule-cues` command.
* Added a five event synthetic fixture with manually calculated expected outputs.
* Tested both MOT17 and KITTI event collections.

### Main Mapping Decisions

* Mapping inputs are limited to the range `[0, 1]`.
* Mapping precision is defined by the preset.
* Every valid event produces either a cue or an explicit suppression.
* Suppressed events are never silently removed.
* Mapping settings are technical configuration and do not establish perceptual quality.

### Audio Rendering

* Added renderer configuration and schema `0.1.0`.
* Added cue package and renderer validation.
* Implemented deterministic sample placement.
* Implemented fixed phase sine synthesis.
* Added attack and release envelopes.
* Added stereo pan.
* Added deterministic overlap mixing.
* Added conditional peak gain.
* Added PCM16 conversion.
* Produced deterministic WAV files.
* Added render logs and renderer metadata.

### Renderer Decisions

* Cue end samples are exclusive.
* Time to sample conversion uses decimal half up rounding.
* Empty valid schedules produce a valid zero frame WAV.
* Class modifiers remain retained for traceability.
* Cross platform byte identity is not claimed without testing.

### Real Dataset Results

MOT17 produced:

* 30,003 valid events
* 26,960 cues
* 3,043 intentional suppressions
* 26,960 rendered cues
* 885,822 stereo frames at 44,100 Hz

KITTI produced:

* 1,089 valid events
* 711 cues
* 378 `DontCare` suppressions
* 711 rendered cues
* 680,022 stereo frames at 44,100 Hz

### Repeatability And Traceability

For both datasets:

* repeated runs produced the same event, cue and audio run IDs
* event, cue and audio files were byte identical
* all recorded hashes matched
* no eligible events were missed
* no cues were unlinked
* source and render links agreed
* generated evidence contained no private dataset paths

### Verification

* Ruff passed.
* 184 tests excluding integrations passed.
* Both private integrations passed.
* 55 focused Stage 2 tests passed.
* All 186 tests passed.

### Outcome

Both datasets were converted from validated events into deterministic cue schedules and WAV outputs with retained provenance.

Stage 2 was complete.

## 6 To 17 August 2026: Stage 3 Technical Evaluation

Stage 3 defined, tested and applied the technical evaluation method.

### Define And Test The Evaluation

* Added Technical Evaluation Contract `0.1.0`.
* Added the evaluation report schema.
* Defined event accounting and coverage.
* Defined timing alignment measures.
* Defined traceability checks.
* Defined cue density measures.
* Defined overlap measures.
* Defined repeatability checks.
* Created a five event synthetic test case.
* Manually calculated the expected results.
* Added deliberate faults for missed cues, orphan cues, conflicting outcomes, broken provenance and timing errors.

### Main Evaluation Decisions

* Intentional suppressions are separate from missed events.
* Multiple cues may represent one event.
* An event cannot be both represented and suppressed.
* Zero denominators return `null`.
* Timing uses event, schedule and rendered sample references.
* Repeatability evidence is separated into semantic, file byte, audio and configuration checks.

### Synthetic Test Results

The manual test case produced:

* eligible coverage `4 / 4`
* source representation `4 / 5`
* suppression `1 / 5`
* accounting completeness `5 / 5`
* missed eligible events `0 / 4`
* peak concurrency `2`
* overlap duration `1.2` seconds

The evaluator reproduced the expected results.

### Real Dataset Evaluation

Technical Evaluation Contract `0.1.0` was applied unchanged to both retained dataset evidence chains.

#### MOT17

* 30,003 valid events
* 26,960 represented events
* 3,043 intentional suppressions
* 0 missed eligible events
* 100% accounting completeness
* 100% eligible event coverage
* 1,342.18 cues per second
* peak concurrency 203
* normalised overlap burden 160.06
* no broken traceability links

#### KITTI Tracking

* 1,089 valid events
* 711 represented events
* 378 intentional suppressions
* 0 missed eligible events
* 100% accounting completeness
* 100% eligible event coverage
* 46.11 cues per second
* peak concurrency 24
* normalised overlap burden 4.53
* no broken traceability links

### Timing

All sample placement errors were zero for both datasets.

MOT17 contained very small decimal differences when timing was expressed in seconds, but these did not alter rendered sample positions.

### Reporting Audit

The final reporting evidence was checked against the canonical evaluation reports.

The audit covered:

* 134 reported values
* 136 table cells
* 12 principal claims
* 23 generated file hashes

No remaining numerical, provenance or private path mismatch was found.

Repeated reporting builds produced identical files.

### Verification

* Ruff passed.
* 252 tests excluding integrations passed.
* All private evaluation integrations passed.
* All 255 configured tests passed.

### Outcome

Stage 3 provided technical evidence for RQ3 covering accounting, timing, traceability, density, overlap and repeatability.

The evaluation does not provide participant or perceptual evidence.

Stage 3 was complete.

## 20 July To 18 August 2026: Stage 4 Workbench Development

Stage 4 assembled the retained evidence into a read only inspection workbench.

### Session Validation

* Added Workbench Session Contract `0.1.0`.
* Added deterministic session identity.
* Added validation across event, cue, audio and evaluation evidence.
* Added runtime media binding.
* Prevented private machine paths from entering session identities and diagnostics.

### Runtime Correction

Initial validation incorrectly assumed that event, cue and audio packages were stored under one shared output directory.

The retained evidence used separate package directories.

The runtime binding was corrected and tested without changing Stage 1 to 3 evidence.

Both retained sessions then validated with stable session identities.

### Inspection Interface

* Added the local inspection service.
* Added the browser interface.
* Displayed source frames and bounding boxes.
* Played the retained WAV without modification.
* Used audio playback time as the single synchronisation clock.
* Displayed events, cues and suppressions.
* Displayed provenance information.
* Displayed retained technical evaluation results.

### Add KITTI Support

* Added the retained KITTI session.
* Added a two session catalogue.
* Added a dataset selector.
* Used the same validation and browser architecture for both datasets.
* Added cross dataset session switching tests.

### Browser Problems Found

Researcher inspection identified several technical interface problems:

* dense timeline rendering caused unnecessary browser work
* cue controls could change order
* only the first ten cues on some frames were displayed
* final frame cues could be unavailable
* cue selection did not always update the displayed time
* represented bounding boxes were not directly selectable

### Corrections

* Cached the static timeline marker layer.
* Limited frame processing to frame changes.
* Added bounded frame preloading.
* Made cue ordering deterministic.
* Displayed every retained cue on the current frame.
* Corrected final frame cue selection.
* Updated transport values immediately after selection.
* Made represented bounding boxes select their exact retained cue.
* Kept suppressed and anomalous boxes as contextual evidence.
* Added keyboard operation for represented boxes.
* Simplified interface terminology and help.

None of these corrections changed the retained event records, cue schedules, WAV files or Stage 3 findings.

### Final Browser Checks

The researcher completed final Firefox and Chrome checks using both retained datasets.

The checks covered:

* source imagery
* bounding boxes
* audio playback
* synchronisation
* cue selection
* provenance
* suppression behaviour
* final frame inspection
* technical metrics
* session switching
* privacy
* path free error handling

These were engineering checks rather than participant usability or accessibility testing.

### Outcome

The workbench could inspect both retained dataset cases through the same validated interface.

Stage 4 was complete on 18 August 2026.

## 19 August To 3 September 2026: Stage 5 Report And Submission Preparation

### Dissertation Drafting

* Drafted Methodology And Research Design.
* Drafted Workbench Design And Implementation.
* Drafted Technical Evaluation And Results.
* Drafted Discussion.
* Drafted Conclusion And Future Work.
* Added the Introduction.
* Added the Literature Review.
* Added Ethical Considerations And Critical Reflection.
* Added the Abstract.
* Added the UWE Harvard reference list.

### Academic Review

* Integrated citations across the dissertation.
* Confirmed all three research questions were addressed.
* Verified cited sources against the reference list.
* Reviewed claims against retained evidence.
* Preserved the project limitations and evidence boundaries.
* Confirmed no Stage 1 to 4 research evidence was changed during report preparation.

### Word Count And Final Document

The working manuscript was reduced from approximately 8,603 words to a final formatted count within the required assessment limit.

The reduction preserved:

* all three research questions
* project objectives
* technical evaluation findings
* ethical boundaries
* threats to validity
* documented limitations

The final Word and PDF versions were prepared and visually reviewed.

### References

The reference audit confirmed that cited sources and reference entries matched in both directions.

### Outcome

The dissertation and artefact were prepared for submission.

## 21 To 28 August 2026: Hosted Workbench And Final Review

### Hosted Deployment

* Added a hosted Render deployment.
* Replaced initial demonstration content with the two retained verified sessions.
* Required a verified retained bundle and expected SHA 256 value.
* Prevented fallback to unverified synthetic evidence.
* Added dataset attribution.
* Recorded the live hosted route in repository guidance.

The hosted interface remained a read only copy of the existing inspection evidence.

It did not regenerate research outputs or create new evaluation evidence.

### Supervisor Feedback

Supervisor feedback focused on:

* alignment with the marking criteria
* clear report presentation
* a focused viva
* concentration on the main project outcomes

Positive feedback was recorded without treating it as a grade or assessment result.

## 2 To 3 September 2026: Final Checks And Submission Readiness

### Work Completed

* Consolidated technical documentation.
* Simplified repository navigation.
* Reviewed provenance records.
* Reviewed citation metadata.
* Reviewed dataset attribution.
* Reviewed the hosted workbench boundary.
* Reproduced the reporting file hashes in an isolated checkout.
* Reproduced both canonical evaluation report hashes.
* Validated both retained workbench sessions.
* Validated the hosted bundle checksum.

