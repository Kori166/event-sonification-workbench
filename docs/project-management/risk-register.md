# Risk Register

| ID | Risk | Likelihood | Impact | Mitigation | Status |
|---|---|---|---|---|---|
| R1 | Loss of repository or local project files | Low | High | Use GitHub as the primary version-controlled repository and maintain regular local backups. | Reduced; monitor |
| R2 | Rebuild work reduces the time available for evaluation and writing | Medium | High | Keep the scope limited to MOT17 and KITTI Tracking and prioritise essential deliverables. | Open |
| R3 | Dataset formats or local paths prevent reproducible execution | Medium | Medium | Document paths in `.env.example`, use fixed fixtures and record dataset versions and hashes. | Open |
| R4 | Cue density or overlap makes outputs difficult to evaluate technically | Medium | Medium | Use configurable suppression rules and measure cue density and overlap burden. | Open; Stage 2 |
| R5 | Evaluation metrics confuse intentionally suppressed events with missed events | Medium | High | Define metric terms before implementation and test them using controlled fixtures. | Open; Stage 3 |
| R6 | Generated outputs differ between repeated runs | Low | High | Use deterministic processing, fixed configuration, hashes and repeat-run tests. | Open |
| R7 | The common event schema overfits MOT17 and requires disruptive changes for KITTI Tracking | Medium | High | Retain shared core fields, preserve dataset-specific metadata and review the schema against both formats before freezing it. | Open; mitigated by schema version `0.1.0` |
| R8 | GitHub Issues and project records drift from the actual implementation status | Medium | Medium | Update the project plan, progress log and relevant decision records whenever an issue is completed or the scope changes. | Reduced; monitor |
| R9 | Dataset licensing or redistribution restrictions are overlooked when fixtures are created | Low | High | Commit only minimal fixtures where permitted and document their source, selection method and testing purpose. | Open |

## Review

Last reviewed: 29 July 2026, after completion of Stage 1 Milestone 1.

The register must be reviewed when a risk changes, a mitigation is applied, an issue changes the agreed scope or a new project stage begins.
