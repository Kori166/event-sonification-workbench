# Deterministic Cue Schedule

## Input gate

`schedule-cues` accepts a complete Stage 1 event-package directory, a validated versioned preset,
the common event schema and an output root. It refuses:

- missing, additional, symbolic-link or non-file package entries;
- non-canonical or malformed package JSON;
- package hash, run-ID, event-count or validation-summary inconsistencies;
- a package not recorded as valid;
- events that fail current schema `0.2.0` and semantic validation;
- events not stored in deterministic Stage 1 order;
- a mismatched schema file or preset schema version; and
- parent-traversing, symbolic-link or otherwise unsafe output locations.

Schema and semantic checks reuse the collection validator. Revalidation of a packaged collection
does not open the private source annotation: Stage 1 already verified that physical source and
recorded its hash, while the package gate verifies the package files and provenance. The existing
parser/Stage 1 validation path continues to verify source files by default.

## Event accounting and order

Events are copied into the existing deterministic order:

```text
dataset, sequence, frame, track_id, source_row, event_id
```

The mapper never modifies or reorders the supplied collection. Each sorted event produces exactly
one scheduled cue or one suppression record. Cue and suppression logs independently preserve the
relative event order. Counts in metadata prove `event_count = cue_count + suppression_count`.

## Cue record contract

Each cue records:

- stable `cue_id` and `source_event_id`;
- dataset, sequence, frame, track, common class, source file and source row;
- start time, duration, frequency, amplitude, stereo pan and class modifier; and
- preset name, version and exact-file SHA-256.

The cue ID is `cue:` plus the first 24 lowercase hexadecimal characters of the canonical SHA-256
over source event ID, preset name/version/hash and mapper name/version. It contains no wall-clock,
filesystem or random input. Source event IDs remain the authoritative row-level traceability link.

Suppression records retain the same source and preset provenance plus a stable suppression code and
human-readable reason. Codes are `dont_care_excluded`, `class_not_included`, `class_excluded`,
`confidence_below_minimum` and `frame_stride`.

## Output package

The command writes an ignored directory:

```text
outputs/<cue-run-id>/
|-- cue_schedule.json
|-- cue_schedule.csv
|-- cue_log.json
|-- suppression_log.json
`-- sonification_metadata.json
```

JSON uses compact canonical UTF-8. CSV uses UTF-8, LF endings and this fixed column order:

```text
cue_id,source_event_id,dataset,sequence,frame,track_id,object_class,
start_time_seconds,duration_seconds,frequency_hz,amplitude,stereo_pan,class_modifier,
preset_name,preset_version,preset_sha256,source_file,source_row
```

The displayed header wraps only for readability. The physical header is one line.

`cue_log.json` records every emitted cue parameter, source reference and scheduled status.
`suppression_log.json` accounts for every excluded event. `sonification_metadata.json` records
input event-package identity and file hashes,
preset identity/path/hash/schema hash, mapper identity, schema version, counts, mapping methods,
rule priority, event order and all non-self output hashes.

The cue run ID is content-derived from the input-package identity, exact preset, mapper identity and
event order. Wall-clock time and machine paths are excluded. The metadata file cannot embed its own
hash recursively; the writer returns that exact-byte hash and states the hash scope in metadata.

## Command

```bash
python -m event_sonification_workbench.cli schedule-cues \
  --event-package outputs/<stage-1-run-id> \
  --preset configs/sonification/presets/baseline-v0.1.0.json \
  --output-directory outputs
```

Repeated calls with identical package and configuration produce the same run ID and byte-identical
files. This milestone produces schedules and logs only. It does not generate WAV files, render or
play audio, calculate Stage 3 metrics or establish perceptual validity.
