# Risk Register

| ID | Risk | Likelihood | Impact | Mitigation I will apply | Status |
|---|---|---|---|---|---|
| R1 | Loss of repository or local project files | Low | High | I will use GitHub as the primary version-controlled repository and maintain regular local backups. | Reduced; monitor |
| R2 | Rebuild work reduces the time available for evaluation and writing | Medium | High | I will keep the scope limited to MOT17 and KITTI Tracking and prioritise essential deliverables. | Open |
| R3 | Dataset formats or local paths prevent reproducible execution | Medium | Medium | I will document paths in `.env.example`, use fixed fixtures and record dataset versions and hashes. | Open |
| R4 | Cue density or overlap makes outputs difficult to evaluate technically | Medium | Medium | I will use configurable suppression rules and measure cue density and overlap burden. | Open; Stage 2 |
| R5 | Evaluation metrics confuse intentionally suppressed events with missed events | Medium | High | I will define metric terms before implementation and test them using controlled fixtures. | Open; Stage 3 |
| R6 | Generated outputs differ between repeated runs | Low | High | I will use deterministic processing, fixed configuration, hashes and repeat-run tests. | Open |
| R7 | The common event schema overfits MOT17 and requires disruptive changes for KITTI Tracking | Medium | High | I will retain shared core fields, preserve dataset-specific metadata and review the schema against both formats before freezing it. | Open; mitigated by schema version `0.1.0` |
| R8 | GitHub Issues and project records drift from the actual implementation status | Medium | Medium | I will update the project plan, progress log and relevant decision records whenever I complete an issue or change the scope. | Reduced; monitor |
| R9 | I overlook dataset licensing or redistribution restrictions when creating fixtures | Low | High | I will commit only minimal fixtures where permitted and document their source, selection method and testing purpose. | Open |

## Review

I last reviewed this register on 29 July 2026 after completing Stage 1 Milestone 1.

I will review it again when a risk changes, I apply a mitigation, an issue changes the agreed scope or I begin a new project stage.
