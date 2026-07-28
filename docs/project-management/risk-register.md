# Risk Register

| ID | Risk | Likelihood | Impact | Mitigation | Status |
|---|---|---|---|---|---|
| R1 | Loss of repository or local project files | Low | High | Use GitHub as the primary version-controlled repository and keep regular local backups. | Open |
| R2 | Rebuild work reduces time available for evaluation and writing | Medium | High | Keep the scope limited to MOT17 and KITTI Tracking and prioritise essential deliverables. | Open |
| R3 | Dataset formats or local paths prevent reproducible execution | Medium | Medium | Document required paths in `.env.example`, use fixed samples and record dataset versions. | Open |
| R4 | Cue density or overlap makes outputs difficult to evaluate technically | Medium | Medium | Use configurable suppression rules and measure cue density and overlap burden. | Open |
| R5 | Evaluation metrics confuse intentionally suppressed events with missed events | Medium | High | Define metric terms before implementation and test them using controlled fixtures. | Open |
| R6 | Generated outputs differ between repeated runs | Low | High | Use deterministic processing, fixed configuration, hashes and repeat-run tests. | Open |

The register will be reviewed when a risk changes, a mitigation is applied or a new project stage begins.
