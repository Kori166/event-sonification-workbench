# Manual Independent Report-Evidence Audit

## Status

**Pass, 6 August 2026.** Zero remaining mismatches were observed after the two defects described
below were corrected and the complete reporting package was regenerated.

This audit was performed independently of the reporting generator. Read-only audit calculations
loaded the canonical JSON records directly, used separately written pointer/formula logic and checked
the presentation files. The reporting module was not imported. SVGs were also rendered in a local
headless browser and inspected visually; the temporary raster previews were deleted from the task
scope and are not repository evidence.

## Source integrity

| Dataset | Canonical report SHA-256 | Result |
|---|---|---|
| MOT17-02-DPM | `d847e805d0b2d7ccd50cd315bbcecfc0ad525f40e7c4c2013938f955d20f13e5` | Match |
| KITTI Tracking 0000 | `b5589590a8c645bd7b5654d0318bf90fdb412f987719c26c2374bf3e487f9ff2` | Match |

Both source files retained these hashes after generation and audit.

## Independent arithmetic

The following calculations used literal source operands transcribed from the canonical records, not
the generator's derived output.

| Calculation | Independently calculated value | Canonical value | Result |
|---|---:|---:|---|
| MOT17 source representation, `26,960 / 30,003` | 0.8985768089857681 | 0.8985768089857681 | Match |
| MOT17 suppression rate, `3,043 / 30,003` | 0.10142319101423192 | 0.10142319101423192 | Match |
| MOT17 cues per second, `26,960 / 20.086666666666666` | 1342.1838698971126 | 1342.1838698971126 | Match |
| MOT17 normalised burden, `3215.1133333333332 / 20.086666666666666` | 160.0620643876535 | 160.0620643876535 | Match |
| KITTI source representation, `711 / 1,089` | 0.6528925619834711 | 0.6528925619834711 | Match |
| KITTI suppression rate, `378 / 1,089` | 0.34710743801652894 | 0.34710743801652894 | Match |
| KITTI cues per second, `711 / 15.42` | 46.10894941634241 | 46.10894941634241 | Match |
| KITTI normalised burden, `69.9 / 15.42` | 4.53307392996109 | 4.533073929961089 | Match within binary-float representation tolerance; canonical raw decimal preserved |

## Complete presentation audit

| Scope | Checked | Mismatches |
|---|---:|---:|
| Manifested values reached by tables and figures | 134 | 0 |
| Principal table rows | 32 | 0 |
| Supplementary timing rows | 36 | 0 |
| Table data cells across CSV and Markdown | 136 | 0 |
| Figure source-data points | 20 | 0 |
| Principal claim rows | 12 | 0 |
| Table and figure captions | 7 | 0 |
| Hash-manifest file entries | 23 | 0 |

Every principal CSV row was recalculated against the report or repeat-comparison record identified by
its manifest entry. Every corresponding Markdown row was then compared cell-for-cell with the CSV.
The same check covered all 36 rows of the complete timing supplement. The audit confirmed that
eligible-event coverage and source representation use their different contract denominators.

For Figure 1, all eight outcome counts and all eight proportions were recalculated from valid-event
denominators, including the zero-width missed and excluded categories. The two cue-density and two
normalised-overlap plotted values were checked against their canonical scalars. Visual inspection
confirmed zero-based axes, readable value labels, restrained styling and no overlapping text after
the layout correction.

All 12 bounded claims were present in the claim matrix and linked to manifested evidence. The RQ3
findings retain the small non-zero MOT17 seconds-domain values and exact sample-placement distinction.
No claim that all timing errors were zero appears. All four table captions and three figure captions
state their scope, units or denominators and interpretation limits.

The terminal hash manifest contained 23 entries and every recorded byte size and SHA-256 was
recalculated successfully. Its own SHA-256 is
`ee7c773fc14274f69f69a74878795c297e0a3d928fdc1c705221f3cd72b3942d`; the self-hash exclusion is
structural and documented.

## Defects found and resolved

1. Initial visual inspection found that Figure 1's second count annotation collided with the
   percentage-axis labels and that the MOT17 label was redundant. The deterministic SVG layout was
   corrected, regenerated and reinspected.
2. Initial arithmetic inspection found that recalculating KITTI normalised overlap burden through a
   binary float produced `4.53307392996109`, whereas the canonical JSON retains
   `4.533073929961089`. The generator was changed to preserve canonical raw scalar values while
   auditing formulas separately. The displayed two-decimal value did not change.
3. Two early audit-script runs stopped on audit-side parsing assumptions: the Markdown separator was
   incorrectly counted as a data row, and a required phrase was searched without normalising a line
   break. Corrected independent checks passed; neither issue changed presentation evidence.

## Boundary

This audit establishes numerical and provenance agreement for the two selected case studies under
the fixed contract, preset, renderer and recorded environment. It does not establish perceptual
quality, participant outcomes, accessibility, usability, navigation, mobility, safety or
cross-environment byte identity.
