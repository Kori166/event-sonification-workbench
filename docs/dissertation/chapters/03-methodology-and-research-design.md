# 3. Methodology and Research Design

## 3.1 Research approach

This project used an iterative design-and-evaluation methodology to construct and examine an event-based sonification workbench. The research artefact is a deterministic pipeline that transforms public video annotations into normalised events, maps eligible events to audio cues, renders those cues, and exposes the resulting evidence for inspection. The method is centred on traceable technical claims: each claim must be supported by a versioned contract, generated artefact, automated check or recorded decision.

Development was divided into four implementation stages followed by dissertation synthesis. Stage 1 defined the common event schema and dataset adapters. Stage 2 implemented deterministic event-to-cue mapping and audio rendering. Stage 3 froze and applied the technical evaluation contract. Stage 4 integrated the validated chain into a local inspection workbench. Decisions, risks and verification evidence were recorded as the artefact evolved, allowing the final analysis to distinguish implemented behaviour from intended or future work.

## 3.2 Case selection and data

Two public annotated tracking datasets were selected as contrasting technical cases. MOT17-02-DPM supplies a dense pedestrian-tracking sequence at 30 frames per second and uses a compact numeric row format with one-based frame indices. KITTI Tracking sequence 0000 supplies road-scene annotations at 10 frames per second, uses zero-based frames, and includes a broader native ontology and additional fields for truncation, occlusion and three-dimensional geometry. The cases were not sampled to support population inference. They were selected to test whether a common pipeline could preserve and process different annotation conventions.

The raw datasets, full intermediate packages and rendered WAV files were kept outside version control. Reproduction declarations record logical inputs, expected hashes and runtime-root environment variables. This design limits repository size and avoids redistributing source data while retaining checks that connect local inputs to the reported results.

## 3.3 Artefact construction

Each adapter parses its native source, applies explicit index and geometry conversions, preserves source-specific metadata, and emits the same versioned event-package structure. The mapper consumes only validated event packages and a versioned preset. It produces both cue records and explicit suppression records, so ineligible events remain part of the account. The renderer verifies the cue package and emits audio with a sample-level render log. Stable identifiers and content hashes connect all stages.

The integrated workbench reuses these pipeline artefacts rather than recreating their logic in the interface. A versioned session contract declares the event, cue, audio and evaluation inputs. Before serving a session, validation checks the complete chain. The interface is local, read-only and loopback-bound; it provides synchronised visual, auditory, timeline, trace and metric views for technical inspection.

## 3.4 Evaluation method

The Technical Evaluation Contract version 0.1.0 was frozen before the real-data milestones. It defines event outcomes, coverage denominators, three timing domains, traceability requirements, density and overlap calculations, and distinct reproducibility claims. This prevented favourable results from changing the meaning of a metric after observation.

Evaluation proceeded in three layers. First, a small manual oracle tested known event outcomes and sample calculations. Second, focused negative cases tested whether incorrect links, outcomes and sample placements were detected. Third, the two public-data cases were executed through the full chain. Repeated builds tested determinism, while a separate reporting audit compared reports, tables, figures, captions and hashes against the canonical evidence.

The analysis is deliberately bounded to technical evaluation. No participants were recruited, and no perceptual, accessibility or task-performance experiment was conducted. Cue density and overlap are therefore reported as measurable properties of the output rather than proxies for intelligibility or usefulness.

## 3.5 Research quality and scope controls

Reliability was supported by versioned schemas and contracts, deterministic identifiers, fixed renderer policies, automated tests and byte-level comparisons. Validity was supported by keeping source and common meanings separate, making suppressions explicit, using sample-domain timing checks and documenting limitations in a live risk register. The independent reporting audit reduced the risk of transcription drift between machine-readable reports and dissertation-facing artefacts.

The method does not eliminate all threats. One mapping preset, two sequences and one recorded execution platform limit generalisation. The methodological claim is consequently modest: the project demonstrates and technically evaluates a reproducible architecture and procedure, rather than proving an optimal or perceptually validated sonification.

