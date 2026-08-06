# Stage 3 Close-out

## Status and scope

Stage 3 technical evaluation is complete within its defined scope on 6 August 2026. Milestone 1
froze and synthetically verified the evaluation method, Milestone 2 applied it unchanged to two
verified real evidence chains, and Milestone 3 converted the canonical results into deterministic,
audited report-ready material. RQ3 is supported by technical case-study evidence. No participant,
perceptual, accessibility, usability, navigation, mobility or safety validation has been performed,
and the overall project is not yet submission-ready.

Work began from `origin/main` commit `5fcab3ad8465f960e1a217063deb8fa82314fa93`, the merge of PR
#26. The isolated branch is `stage-3-report-ready-evidence`; the reporting generator identity is
commit `21f8cfb163935bce3faf899eefbdaf1a224ceee4`. The separate dirty checkout and both preserved
stashes were not used as evidence or modified.

## Milestone evidence

### Milestone 1: frozen method and oracle

- evaluation contract version: `0.1.0`;
- contract SHA-256: `68513164a731d977988acc34f7013cc3000c78d5e6aa345b2f7bcbe3e346de3e`;
- report schema SHA-256: `bc6be639a9f1939e5797572a405f8cc5b426691da0407d33c3347368cede1b6f`;
- event schema version: `0.2.0`;
- baseline preset and renderer versions: `0.1.0`;
- project-authored manual synthetic oracle: 26 focused tests passed at final close-out.

No contract formula, denominator, timing rule, overlap rule, event eligibility rule, suppression
rule or threshold was changed in Milestones 2 or 3.

### Milestone 2: canonical real reports

| Dataset and sequence | Evaluation run ID | Canonical physical SHA-256 |
|---|---|---|
| MOT17-02-DPM | `evaluation-mot17-mot17-02-dpm-2636a438409d649e` | `d847e805d0b2d7ccd50cd315bbcecfc0ad525f40e7c4c2013938f955d20f13e5` |
| KITTI Tracking 0000 | `evaluation-kitti_tracking-0000-d997cdc8f6467c1d` | `b5589590a8c645bd7b5654d0318bf90fdb412f987719c26c2374bf3e487f9ff2` |

Both hashes were recalculated before reporting generation and after the final audits. Both reports
validated against the frozen schema, retained contract `0.1.0`, matched their dataset summaries and
retained semantic and byte identity across three isolated repetitions. The shared experiment and
environment identities remained
`320e0054c670fe5fd4c422aff52d5f9cada49853073e0d5bed9fcbabf1bc2733` and
`02c902984008d0499ad1b2f3f5bae4fef54937f51ff9de4450a5c6aae32fa949`.

### Milestone 3: report-ready package

The canonical build command was:

```text
python -m event_sonification_workbench.cli generate-stage3-report-evidence \
  --mot17-report docs/evaluation/evidence/mot17/mot17_technical_evaluation_report.json \
  --kitti-report docs/evaluation/evidence/kitti/kitti_technical_evaluation_report.json \
  --output docs/evaluation/reporting
```

The generator verified the source/configuration hashes and report schemas before writing. Its
presentation manifest contains 134 values: 104 direct and 30 derived. Each records its report and
evidence-record identity, evaluation run, JSON Pointer, raw/display values, numerator, denominator,
formula, formatting rule, interpretation boundary and audit status.

- reporting-evidence manifest SHA-256:
  `5de4e72aa9dc014aa714a206879a3f5674abf1b1400c0f0fc5198761e0a73c66`;
- terminal generated-file hash-manifest SHA-256:
  `ee7c773fc14274f69f69a74878795c297e0a3d928fdc1c705221f3cd72b3942d`;
- automated audit JSON SHA-256:
  `cb90bd0b373ab6d5e1ab5d36515958257d47fb18229fbe0688bf7e7beb1c1cf1`.

## Report-ready table identities

| File | SHA-256 |
|---|---|
| `tables/table-1-event-accounting-and-coverage.csv` | `45d822f174a05876dcbee37f75c3611b687c27c74340526ab4097eb229895090` |
| `tables/table-1-event-accounting-and-coverage.md` | `d78fb08bde418a7726e39fa1af18fa56ce253a8c82061a949d2bdd0f0a5e077e` |
| `tables/table-2-timing-traceability-reproducibility.csv` | `2376ced7699185c0b8fd92555742aaa544a859002ab95727585fef00ae81da72` |
| `tables/table-2-timing-traceability-reproducibility.md` | `7ff0dbc670e540b2c84d58f5400f2a96f0422ef5361682b84026d57fe6a5c542` |
| `tables/table-2a-complete-timing-statistics.csv` | `7018d5678b7cb2df9b2004c85646d9559e461c61e08a95acff11a39c459efc19` |
| `tables/table-2a-complete-timing-statistics.md` | `7f4c69528deb00c07f33acaa042532e5d68a5d21b6c13456277c0905e697e571` |
| `tables/table-3-density-and-overlap.csv` | `d813279a53915b6b4ef0fda544deb18c70e7e64c58f50adf494eb3c06c4644e1` |
| `tables/table-3-density-and-overlap.md` | `d1380bdb7f6b5409b70ca60081f8010b76a6885ee94a9039e1b3e1bea1680152` |
| `tables/table-captions.md` | `a7a5b5adf11626861c6501a9cbcbdb5c1e6886f5d15f33eaa216542b4db27496` |

## Deterministic figure identities

| File | SHA-256 |
|---|---|
| `figures/figure-1-event-outcomes-data.csv` | `c5579e3fdf74ae7e4322f4fe9b0f72b230b6c0b193885745aa61e2aa08aa728e` |
| `figures/figure-1-event-outcomes.svg` | `4e78207372c3013a4b95e86f43a36f711c1f77c2cfff3beadf8fedeefa978ca1` |
| `figures/figure-2-cue-density-data.csv` | `8093909b4540f135f1daf8c396557cc74e060ed877354804e82c57c38f798614` |
| `figures/figure-2-cue-density.svg` | `73e9d26bad703228ce6e562842b4961b6bbe3a1e8cd1511c34682971b7b2ef54` |
| `figures/figure-3-overlap-burden-data.csv` | `f80478fe190ad246edb7918d931e7cbd82b06f03afef1860500e65e2f0bded97` |
| `figures/figure-3-overlap-burden.svg` | `991afc1836e575d36e3697a68ae23524b543c7a9681876346ad2d24edd67b823` |
| `figures/figure-captions.md` | `6de9e09e328e1e1a8652d814f839c2d492c9971ef001f1b48a0cf05260542d78` |

The SVGs use fixed element ordering and identifiers, no generated metadata, restrained print-friendly
styling and zero-based comparison axes. Visual inspection found and resolved one Figure 1 text
collision before these hashes were accepted.

## Audit and reproducibility results

The automated audit passed with:

- 134 values checked;
- 104 direct and 30 derived values;
- 136 table data cells;
- 20 figure data points;
- 12 principal claims;
- zero mismatches, missing sources, formatting failures, private-path matches and prohibited files;
- complete table-to-manifest, figure-to-manifest and claim-to-evidence links; and
- unchanged canonical source hashes.

The independent audit separately recalculated the required source-representation, suppression,
density and normalised-overlap values, checked every row of the three principal tables and timing
supplement in CSV and Markdown, checked every plotted datum, all 12 claims, all seven captions and
all 23 terminally recorded file hashes. It passed with zero remaining mismatches. One initial raw-
value precision discrepancy was fixed by preserving the canonical KITTI scalar while auditing its
division formula separately.

The CLI was then run twice into separate empty temporary directories. Both commands exited zero,
produced the same 24-file set and were byte-identical for every JSON, CSV, Markdown and SVG file.
Both builds reproduced the reporting manifest and terminal hash-manifest identities above.

## Final quality gates

| Command | Exit | Passed | Failed | Skipped | Deselected |
|---|---:|---:|---:|---:|---:|
| `python -m ruff check .` | 0 | n/a | 0 | n/a | n/a |
| `python -m pytest tests/test_technical_evaluation.py -q` | 0 | 26 | 0 | 0 | 0 |
| `python -m pytest -m "not integration"` | 0 | 252 | 0 | 0 | 3 |
| `python -m pytest -m integration` with all three private roots configured | 0 | 3 | 0 | 0 | 252 |
| `python -m pytest` with all three private roots configured | 0 | 255 | 0 | 0 | 0 |

An initial integration invocation without the private variables selected three tests but skipped all
three; it was explicitly rejected as pass evidence. A second invocation with the two dataset roots
passed two tests and skipped the retained-chain test because its third root was absent; it too was
not used as final pass evidence. The final configured integration and complete-suite rows above had
no skips.

## Bounded RQ3 answer

Event-based sonification outputs can be evaluated reproducibly by fixing event-outcome categories
and denominators, measuring scheduling/render/end-to-end alignment separately in sample and seconds
domains, resolving event-to-source/render provenance, quantifying rendered-timeline cue density and
overlap, and comparing semantic and canonical bytes across isolated repetitions. In the selected
MOT17-02-DPM and KITTI Tracking 0000 chains, the method produced complete contract-defined
accounting, no missed eligible events, exact sample placement, complete required traceability and
repeat-identical reports in the recorded environment.

This does not mean every source event was sonified: source representation was lower than eligible-
event coverage because intentional suppressions were present. MOT17 also retained very small non-
zero seconds-domain differences despite zero sample-domain statistics. The measured density and
overlap differences describe the fixed baseline's technical load, not perceptual quality or listener
performance.

## Files included and excluded

Included work consists of the reporting generator and CLI, focused tests, Decision 0015, the
reporting policy, value manifest, report-ready tables/figures/captions, claim matrix, RQ3 method and
findings, automated/manual audits, replacement note and reconciled project records.

Deliberately excluded were the full private datasets, full Stage 1/2 package chains, evaluator
inputs, WAV files, generated raster previews, temporary repeat directories, `.env`, physical dataset
paths, usernames, images, videos, audio and unrelated interface work. Canonical Milestone 2 reports,
contract `0.1.0` and its schemas were not modified.

## Limitations and handover

- Only MOT17-02-DPM and KITTI Tracking 0000 were evaluated; they are selected case studies.
- Dataset annotation conventions and scene composition differ.
- One baseline preset and one baseline renderer were evaluated; no alternative mapping comparison
  was conducted.
- No participant test, perceptual quality measure or accessibility, usability, navigation, mobility
  or safety outcome exists.
- High eligible-event coverage does not mean all source events were sonified; intentional
  suppression is not failure.
- High density or overlap does not establish poor perceptual performance.
- Byte identity is limited to the recorded environment; no cross-environment result exists.

The exact next milestone is **Stage 4 Milestone 1: assemble a versioned artefact release candidate
and verify installation, configuration, evidence availability and end-to-end execution from a clean
environment.**
