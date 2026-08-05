# Generated Outputs

The output writer creates ignored deterministic packages beneath this directory:

```text
outputs/<run-id>/
```

Each run contains `events.json`, `events.csv`, `run_metadata.json` and `provenance_log.json`.
Generated packages may contain complete private-dataset-derived event collections and must not be
committed. See `docs/data-model/output-package.md` for the format and reproduction contract.
