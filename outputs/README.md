# Generated Outputs

The output writer creates ignored deterministic packages beneath this directory:

```text
outputs/<run-id>/
```

Stage 1 event runs contain `events.json`, `events.csv`, `run_metadata.json` and
`provenance_log.json`. Stage 2 scheduling runs contain `cue_schedule.json`, `cue_schedule.csv`,
`cue_log.json`, `suppression_log.json` and `sonification_metadata.json`. Stage 2 audio runs contain
`sonification.wav`, `render_log.json` and `renderer_metadata.json`.

Generated packages may contain complete private-dataset-derived event collections or derived cue
schedules and must not be committed. See `docs/data-model/output-package.md` and
`docs/data-model/cue-schedule.md` for the event and cue contracts, and
`docs/data-model/audio-rendering.md` for the audio contract.

Two independently generated packages of the same kind can be checked without recording physical
paths:

```text
python -m event_sonification_workbench.cli compare-packages \
  --left-package <first-package> \
  --right-package <second-package>
```

The deterministic comparison report covers every expected file using exact bytes and SHA-256. A
mismatch names the affected file and both hashes and returns a nonzero command status.
