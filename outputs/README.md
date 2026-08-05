# Generated Outputs

The output writer creates ignored deterministic packages beneath this directory:

```text
outputs/<run-id>/
```

Stage 1 event runs contain `events.json`, `events.csv`, `run_metadata.json` and
`provenance_log.json`. Stage 2 scheduling runs contain `cue_schedule.json`, `cue_schedule.csv`,
`cue_log.json`, `suppression_log.json` and `sonification_metadata.json`.

Generated packages may contain complete private-dataset-derived event collections or derived cue
schedules and must not be committed. See `docs/data-model/output-package.md` and
`docs/data-model/cue-schedule.md` for the two format contracts.
