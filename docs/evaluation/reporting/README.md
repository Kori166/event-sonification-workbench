# Stage 3 Reporting Evidence

This directory separates dissertation-ready presentation derivatives from the canonical technical-
evaluation evidence in `docs/evaluation/evidence/`. The reporting build reads the canonical MOT17
and KITTI report JSON files, verifies their committed SHA-256 identities, validates them against the
frozen report schema and writes only selected presentation values. It does not rerun or redefine the
evaluation.

## Source hierarchy

Values are resolved in this order:

1. canonical technical-evaluation report JSON;
2. report schema and contract `0.1.0`;
3. evaluator-input, experiment and environment manifests;
4. reproducibility comparisons and traceability audits;
5. dataset JSON and CSV summaries;
6. Markdown summaries and close-out prose.

The canonical reports are:

- `docs/evaluation/evidence/mot17/mot17_technical_evaluation_report.json`, SHA-256
  `d847e805d0b2d7ccd50cd315bbcecfc0ad525f40e7c4c2013938f955d20f13e5`;
- `docs/evaluation/evidence/kitti/kitti_technical_evaluation_report.json`, SHA-256
  `b5589590a8c645bd7b5654d0318bf90fdb412f987719c26c2374bf3e487f9ff2`.

The presentation-value manifest records a stable ID, source report and hash, evaluation run,
structural JSON Pointer, raw and displayed value, unit, derivation and interpretation boundary for
every table value, figure datum and principal RQ3 finding value.

## Display-format policy

- Counts are integers. Markdown uses thousands separators; CSV and JSON use plain integers.
- Rates retain their exact decimal in the manifest and display as percentages to two decimal
  places. A rate cell includes its numerator and denominator where space permits. A null rate remains
  null and is never presented as zero.
- Cue density displays two decimal places. Exact values remain in the manifest.
- Durations and excess concurrent cue-seconds display six decimal places where needed. Overlap
  proportions display as percentages to two decimal places, normalised overlap burden to two decimal
  places and peak concurrency as an integer.
- Sample-domain timing values display as integers. Seconds-domain zero displays as `0`; a small
  non-zero value uses scientific notation and is never rounded to a displayed zero.
- Full SHA-256 values are retained in manifests and audit files. Prose may abbreviate a hash only
  when the full value is available through the manifest.
- CSV uses UTF-8, a fixed column order, RFC-compatible quoting and LF line endings. JSON uses the
  project's canonical UTF-8 serialisation. SVG identifiers and element order are fixed.

Exact sample placement and exact decimal-second equality are distinct properties. The principal
timing table therefore reports both domains. It must not be summarised as saying that all timing
errors were zero.

## Deterministic build

From the repository root, run:

```text
python -m event_sonification_workbench.cli generate-stage3-report-evidence \
  --mot17-report docs/evaluation/evidence/mot17/mot17_technical_evaluation_report.json \
  --kitti-report docs/evaluation/evidence/kitti/kitti_technical_evaluation_report.json \
  --output docs/evaluation/reporting
```

The output directory may already contain this hand-authored policy file; all generator-owned paths
must otherwise be absent unless `--replace-generated` is supplied. The generator verifies source
hashes and schemas before writing. Identical reports and generator identity produce byte-identical
JSON, CSV, Markdown and SVG outputs. No timestamp, physical machine path or random SVG identifier is
written.

`audits/generated-file-hashes.json` is the terminal hash manifest. It records every other generated
file. It cannot record its own digest without a cryptographic self-reference, so that single
structural exclusion is explicit in the manifest and is verified separately by the close-out audit.

## Interpretation boundary

The package describes MOT17-02-DPM and KITTI Tracking sequence 0000 under one baseline preset and
renderer in the recorded environment. The sequences differ in annotation conventions and scene
composition and are not population samples. No alternative mapping, participant test, perceptual
quality measure, cross-environment byte comparison, or accessibility, usability, navigation,
mobility or safety outcome is present. Intentional suppression is a configured outcome rather than
a missed event, and high technical density or overlap is not evidence of listener difficulty.
