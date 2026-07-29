# Risk Register

| ID | Risk | Likelihood | Impact | Mitigation | Status |
|---|---|---|---|---|---|
| R1 | Loss of repository or local project files | Low | High | Use GitHub as the primary version-controlled repository and maintain regular local backups. | Reduced; monitor |
| R2 | Rebuild work reduces the time available for evaluation and writing | Medium | High | Keep the scope limited to MOT17 and KITTI Tracking and prioritise essential deliverables. | Open |
| R3 | Dataset formats or local paths prevent reproducible execution | Medium | Medium | Use runtime source roots, portable relative paths, fixed fixtures and recorded dataset hashes. | Reduced by MOT17 local-check command; real run pending |
| R4 | Cue density or overlap makes outputs difficult to evaluate technically | Medium | Medium | Use configurable suppression rules and measure cue density and overlap burden. | Open; Stage 2 |
| R5 | Evaluation metrics confuse intentionally suppressed events with missed events | Medium | High | Define metric terms before implementation and test them using controlled fixtures. | Open; Stage 3 |
| R6 | Generated outputs differ between repeated runs | Low | High | Use deterministic processing, fixed configuration, hashes and repeat-run tests. | Open |
| R7 | The common event schema overfits MOT17 and requires disruptive changes for KITTI Tracking | Medium | High | Retain shared core fields, preserve dataset-specific metadata and review the schema against both formats before freezing it. | Open; mitigated by schema version `0.1.0` |
| R8 | GitHub Issues and project records drift from the actual implementation status | Medium | Medium | Update the project plan, progress log and relevant decision records whenever an issue is completed or the scope changes. | Reduced; monitor |
| R9 | Dataset licensing or redistribution restrictions are overlooked when fixtures are created | Low | High | Commit only minimal fixtures where permitted and record source sequence, selected rows, selection purpose and hashes. | Open; fixture not yet committed |
| R10 | A MOT17 evaluation mark is incorrectly treated as detector confidence | Medium | High | Store common confidence as `null`, retain the source mark in metadata and test the rule explicitly. | Reduced by Decision 0007 and tests |
| R11 | Synthetic format tests are reported as evidence of real dataset compatibility | Medium | High | Keep the evidence boundary explicit and require a dataset-derived fixture and local run before milestone completion. | Open until real-data quality gate passes |

## Review

Last reviewed: 29 July 2026, during Stage 1 Milestone 2 implementation.

The register must be reviewed when a risk changes, a mitigation is applied, an issue changes the
agreed scope or a new project stage begins.
