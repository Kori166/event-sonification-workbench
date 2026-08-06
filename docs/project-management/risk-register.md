# Risk Register

| ID | Risk | Likelihood | Impact | Mitigation | Status |
|---|---|---|---|---|---|
| R1 | Loss of repository or local project files | Low | High | Use GitHub as the primary version-controlled repository and maintain regular local backups. | Reduced; monitor |
| R2 | Rebuild work reduces the time available for evaluation and writing | Medium | High | Keep the scope limited to MOT17 and KITTI Tracking and prioritise essential deliverables. | Open |
| R3 | Dataset formats or local paths prevent reproducible execution | Low | Medium | Use runtime source roots, portable relative paths, fixed fixtures and recorded dataset hashes. | Reduced; Stage 1 real packages and both private integrations passed without exposing roots |
| R4 | Cue density or overlap makes outputs difficult to evaluate technically | Medium | Medium | Use configurable suppression rules and measure cue density and overlap burden. | Reduced; contract/oracle verify the measures, real dataset values remain Milestone 2 |
| R5 | Evaluation metrics confuse intentionally suppressed events with missed events | Low | High | Define metric terms before implementation and test them using controlled fixtures. | Reduced; contract `0.1.0`, manual oracle and negative tests freeze the distinction |
| R6 | Generated outputs differ between repeated runs | Low | High | Use deterministic processing, fixed configuration, hashes and repeat-run tests. | Reduced; two independent full event/cue/audio chains for both real datasets were byte- and hash-identical on 6 August 2026 |
| R7 | The common event schema overfits MOT17 and requires disruptive changes for KITTI Tracking | Low | High | Retain shared core fields, preserve dataset-specific metadata and review the schema against both formats before freezing it. | Reduced; schema `0.2.0` review required only a confidence-range relaxation |
| R8 | GitHub Issues and project records drift from the actual implementation status | Medium | Medium | Update the project plan, progress log and relevant decision records whenever an issue is completed or the scope changes. | Reduced; Stage 2 records reconciled with merged PRs #20/#22 and closed Issue #21 at close-out |
| R9 | Dataset licensing or redistribution restrictions are overlooked when fixtures are created | Medium | High | Record dataset-specific terms, attribution, citations, source lines and hashes; exclude full data and media; keep rows private where permission is unresolved. | Active; MOT17 unresolved, KITTI fixture carries official CC BY-NC-SA 3.0 notice |
| R10 | A MOT17 evaluation mark is incorrectly treated as detector confidence | Medium | High | Store common confidence as `null`, retain the source mark in metadata and test the rule explicitly. | Reduced by Decision 0007 and tests |
| R11 | Synthetic format tests are reported as evidence of real dataset compatibility | Low | High | Keep the evidence boundary explicit and require separate private integration runs. | Reduced; both private integrations passed and real package results are recorded separately |
| R12 | A KITTI ranking score is clipped or misreported as a normalised probability | Low | High | Preserve the native value, relax the common range in schema `0.2.0`, document scale semantics and test values outside `[0,1]`. | Reduced by Decision 0008 and automated tests |
| R13 | Stage 2 preset, cue or renderer changes break deterministic sonification | Low | High | Version presets and renderers, canonicalise logs, hash audio outputs and require repeated-run tests. | Reduced; fixture tests and two independent real-data chains reproduce every cue/audio byte and hash; retain regression gates |
| R14 | Floating-point oscillator or mixing implementations differ at a PCM quantisation boundary on another runtime/platform | Medium | Medium | Pin renderer/policy versions, record tested environments and hashes, avoid unsupported cross-platform claims, and add cross-platform evidence before making one. | Open; exact repetition verified on Windows 10.0.26200/AMD64/Python 3.14.3 only; broader-platform evidence remains absent |
| R15 | A technical metric implementation appears plausible but uses the wrong denominator, boundary or percentile rule | Low | High | Freeze formulas before real-data use and compare every result with a manually calculated synthetic oracle plus fault cases. | Reduced by contract `0.1.0`, Decision 0013 and 25 focused tests; retain golden gate |

## Review

Last reviewed: 6 August 2026, at Stage 3 Milestone 1 close-out.

R9 remains an explicit redistribution limitation. R4 is reduced by an implemented method but real
density/overlap values remain unknown until Milestone 2. R5 and R15 are reduced by the frozen manual
oracle gate. R13 is reduced by complete real-data schedule-to-audio repeat evidence. R14 records the
deliberately bounded cross-platform evidence claim and remains open.

The register must be reviewed when a risk changes, a mitigation is applied, an issue changes the
agreed scope or a new project stage begins.
