# Risk Register

| ID | Risk | Likelihood | Impact | Mitigation | Status |
|---|---|---|---|---|---|
| R1 | Loss of repository or local project files | Low | High | Use GitHub as the primary version-controlled repository and maintain regular local backups. | Reduced; monitor |
| R2 | Rebuild work reduces the time available for evaluation and writing | Medium | High | Keep the scope limited to MOT17 and KITTI Tracking and prioritise essential deliverables. | Open |
| R3 | Dataset formats or local paths prevent reproducible execution | Low | Medium | Use runtime source roots, portable relative paths, fixed fixtures and recorded dataset hashes. | Reduced; Stage 1 real packages and both private integrations passed without exposing roots |
| R4 | Cue density or overlap makes outputs difficult to evaluate technically | Medium | Medium | Use configurable suppression rules and measure cue density and overlap burden. | Reduced; frozen measures were applied to both selected real sequences and exact density/overlap values are recorded without a perceptual interpretation |
| R5 | Evaluation metrics confuse intentionally suppressed events with missed events | Low | High | Define metric terms before implementation and test them using controlled fixtures. | Reduced; contract `0.1.0`, manual oracle and negative tests freeze the distinction |
| R6 | Generated outputs differ between repeated runs | Low | High | Use deterministic processing, fixed configuration, hashes and repeat-run tests. | Reduced; two independent full event/cue/audio chains for both real datasets were byte- and hash-identical on 6 August 2026 |
| R7 | The common event schema overfits MOT17 and requires disruptive changes for KITTI Tracking | Low | High | Retain shared core fields, preserve dataset-specific metadata and review the schema against both formats before freezing it. | Reduced; schema `0.2.0` review required only a confidence-range relaxation |
| R8 | GitHub Issues and project records drift from the actual implementation status | Medium | Medium | Update the project plan, progress log and relevant decision records whenever an issue is completed or the scope changes. | Reduced but active; Issue #29 was reopened and Decision 0016, the Stage 4 checklist and Phase 1 record now track the PR #30 merge, PR #31 revert and PR #32 final correction sequence |
| R9 | Dataset licensing or redistribution restrictions are overlooked when fixtures are created | Medium | High | Record dataset-specific terms, attribution, citations, source lines and hashes; exclude full data and media; keep rows private where permission is unresolved. | Active; MOT17 unresolved, KITTI fixture carries official CC BY-NC-SA 3.0 notice |
| R10 | A MOT17 evaluation mark is incorrectly treated as detector confidence | Medium | High | Store common confidence as `null`, retain the source mark in metadata and test the rule explicitly. | Reduced by Decision 0007 and tests |
| R11 | Synthetic format tests are reported as evidence of real dataset compatibility | Low | High | Keep the evidence boundary explicit and require separate private integration runs. | Reduced; native source hashes, both retained package chains and the real evaluator path passed for both selected datasets, separately from CI fixtures |
| R12 | A KITTI ranking score is clipped or misreported as a normalised probability | Low | High | Preserve the native value, relax the common range in schema `0.2.0`, document scale semantics and test values outside `[0,1]`. | Reduced by Decision 0008 and automated tests |
| R13 | Stage 2 preset, cue or renderer changes break deterministic sonification | Low | High | Version presets and renderers, canonicalise logs, hash audio outputs and require repeated-run tests. | Reduced; fixture tests and two independent real-data chains reproduce every cue/audio byte and hash; retain regression gates |
| R14 | Floating-point oscillator or mixing implementations differ at a PCM quantisation boundary on another runtime/platform | Medium | Medium | Pin renderer/policy versions, record tested environments and hashes, avoid unsupported cross-platform claims, and add cross-platform evidence before making one. | Open; Stage 2 audio and Stage 3 reports repeat exactly only in their recorded Windows/AMD64/Python 3.14.3 environments; broader-platform evidence remains absent |
| R15 | A technical metric implementation appears plausible but uses the wrong denominator, boundary or percentile rule | Low | High | Freeze formulas before real-data use and compare every result with a manually calculated synthetic oracle plus fault cases. | Reduced by contract `0.1.0`, Decision 0013, 26 focused oracle tests and unchanged real-data application; retain the golden gate |
| R16 | Private paths or prohibited full-data derivatives enter committed evaluation evidence | Low | High | Keep full chains/inputs/WAVs ignored, commit only bounded reports/manifests/summaries, and scan every object and final diff for path markers. | Reduced; canonical and report-ready generators reject private path shapes, generated evidence reports zero matches and the final branch scan remains mandatory |
| R17 | Dissertation tables, figures or prose drift from canonical technical evidence through copying, rounding or denominator changes | Low | High | Generate presentation derivatives from canonical reports, retain raw values and JSON Pointers, audit every displayed value and maintain a claim-to-evidence matrix. | Reduced; 134 values, 136 table cells, 20 figure data points and 12 claims passed automated and independent audits with zero remaining mismatch |
| R18 | The Stage 4 inspection layer bypasses or weakens Stage 1-3 package validation and presents mismatched evidence as one session | Low | High | Freeze Workbench Session Contract `0.1.0`, reuse the verified cross-stage chain checks, compare declared hashes/identities and reject invalid sessions before UI rendering. | Reduced by Decision 0016 and headless tests; PR #32 reapplies the runtime-root correction after PR #31 reverted the premature PR #30 merge, and retained real-chain validation remains the final Phase 1 acceptance gate |
| R19 | Runtime dataset/output paths, usernames or machine-specific state leak into session identities or frontend diagnostics | Low | High | Keep runtime roots outside the deterministic session payload, resolve only safe logical children and return machine-readable path-free diagnostics. | Reduced by Workbench Session `0.1.0`, package-specific root isolation and path-leakage tests; retained real-chain and final release scans remain required before Phase 1 close-out |
| R20 | A browser demonstration is mistaken for participant or perceptual validation | Medium | High | Define the UI as a read-only inspection and demonstration layer, source Stage 3 metrics from verified reports only and retain explicit evidence-boundary wording in documentation and presentation. | Open; Decision 0016 establishes the boundary before UI implementation |

## Review

Last reviewed: 7 August 2026, during recovery of the Stage 4 Milestone 1 Phase 1 runtime-binding
correction after PR #30 was merged prematurely and reverted by PR #31.

R9 remains an explicit redistribution limitation. R4 is reduced by real technical values but those
values are not perceptual evidence. R5 and R15 are reduced by the frozen manual oracle and unchanged
real-data gate. R13 is reduced by complete real-data schedule-to-audio repeat evidence. R14 records
the deliberately bounded cross-platform claim and remains open. R16 is reduced by ignored storage,
hash manifests, generator validation and path scans, all of which remain mandatory. R17 is reduced
by the deterministic reporting build and separate manual audit; those controls must remain active
when material is transferred into the dissertation.

Stage 4 adds R18-R20. Post-merge review of PR #28 showed that R18 also includes runtime package-layout
compatibility: a valid verification design is insufficient if retained packages cannot be resolved
from their actual storage structure. PR #30 implemented the correction but was merged before private
acceptance and then reverted by PR #31. Issue #29 was therefore reopened and PR #32 reapplies the
same separate event/cue/audio runtime-root design while preserving the verified chain and content-
derived identity. R18 and R19 remain only partially reduced until PR #32 passes clean CI and the
retained real-data Stage 4 integration test passes locally. R20 remains open because the browser layer
has not yet been implemented or demonstrated.

The register must be reviewed when a risk changes, a mitigation is applied, an issue changes the
agreed scope or a new project stage begins.
