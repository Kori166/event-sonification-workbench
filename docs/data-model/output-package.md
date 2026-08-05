# Deterministic Event Output Package

## Purpose and scope

The Stage 1 output writer stores one validated MOT17 or KITTI Tracking sequence as deterministic,
inspectable JSON and CSV with run-level metadata and provenance. It consumes common schema `0.2.0`
events and an optional Issue #4 collection-validation report. It does not perform validation again,
filter events, sonify records, generate audio or calculate evaluation results.

Generated packages are local artefacts and remain ignored by Git. The default layout is:

```text
outputs/
`-- <run-id>/
    |-- events.json
    |-- events.csv
    |-- run_metadata.json
    `-- provenance_log.json
```

## Writer API

`write_event_package` in `event_sonification_workbench.output_package` accepts:

- a collection of common events;
- dataset, sequence, parser, schema and class-mapping versions;
- one logical source-file path and SHA-256;
- logical schema, class-mapping and optional configuration references with hashes;
- an optional `EventCollectionValidationReport`;
- conversion assumptions and decision-record references; and
- an output root directory.

The writer validates package consistency and path safety but deliberately delegates event validity to
Issue #4. If a validation report is supplied, its event count and schema version must match and its
status must be valid. If no report is supplied, metadata records `status: not_provided`.

## Run identifier

The run ID has this form:

```text
run-<dataset>-<sequence>-<16 hex characters>
```

The hexadecimal suffix is derived from canonical JSON containing the output format version, dataset,
sequence, event count, logical source reference, parser identity, sorted configuration references,
validation summary, conversion assumptions, decision records and the JSON/CSV event-output hashes.
It contains no wall-clock time, machine path, username or random value. Identical inputs therefore
select the same package directory.

## Deterministic event ordering

Events are sorted by this tuple before either event file is written:

1. `dataset`;
2. `sequence`;
3. `frame`;
4. `track_id`;
5. `source_row`; and
6. `event_id`.

String fields, including `track_id`, use Unicode lexical order because the common schema represents
track identifiers as strings. Integers use numeric order. `DontCare` track `-1` is therefore stable,
and no assumption that all dataset identifiers are positive integers is introduced. Automated tests
exercise complete MOT17 and KITTI fixtures plus a mixed-dataset ordering key. The supplied collection
is not modified or reordered in memory.

## `events.json`

`events.json` is canonical UTF-8 JSON with no trailing newline. Its stable document shape is:

```json
{
  "event_count": 12,
  "events": [],
  "format_version": "0.1.0",
  "schema_version": "0.2.0"
}
```

The example is shown readably; actual bytes use the shared compact canonical serializer. Every event
contains every common field, including conversion notes and dataset-specific metadata. Object keys
are sorted canonically and array order is the deterministic event order.

## `events.csv`

CSV uses UTF-8, comma delimiters, RFC-style quoting where required and LF (`\n`) line endings. The
fixed column order is the schema `0.2.0` required-field order:

```text
schema_version,event_id,dataset,sequence,frame,timestamp,frame_rate,track_id,
object_class,source_object_class,image_width,image_height,bbox_x,bbox_y,bbox_width,
bbox_height,centre_x,centre_y,centre_x_normalised,centre_y_normalised,bbox_area,
bbox_area_normalised,confidence,visibility,source_file,source_file_sha256,source_row,
parser,parser_version,class_mapping_version,conversion_notes,metadata
```

The displayed order wraps for readability; the physical header is one line. Strings remain strings.
Numbers, booleans and null use canonical JSON scalar spelling. `conversion_notes` and `metadata` use
compact canonical JSON inside quoted CSV cells. This preserves their nested information without
inventing dataset-specific columns.

## `run_metadata.json`

Run metadata is canonical JSON and records:

- output format version and deterministic run ID;
- dataset, sequence and event count;
- logical source file and source SHA-256;
- parser name and version;
- class-mapping version, logical file and hash;
- schema version, logical file and hash;
- validation status and counts when supplied; and
- filenames and SHA-256 values for `events.json`, `events.csv` and `provenance_log.json`.

Embedding the hash of `run_metadata.json` inside itself would be recursive. Its exact-byte hash is
therefore returned in `EventPackageResult.file_sha256`, while the metadata explains that scope.

## `provenance_log.json`

The canonical provenance log records the logical source reference, all configuration references,
parser and schema versions, validation summary, event ordering, sorted conversion assumptions,
decision-record references and hashes for both event outputs. MOT17 packages additionally record the
logical `seqinfo.ini` reference and hash. No dataset root or configuration storage root is written.

The writer rejects absolute Windows, UNC and POSIX paths in event or provenance content. Logical file
references must use relative POSIX paths without `..` traversal. URLs already present as documented
dataset metadata are not mistaken for local paths.

## Determinism and overwrite policy

All four documents omit execution time. Repeated writes with identical inputs produce the same run
ID, event order, bytes and hashes. Rerunning the same package safely replaces its four deterministic
files. A pre-existing run directory containing any unexpected entry, symlink or non-file output path
is rejected rather than silently mixed into the package.

## Command line

With the relevant private dataset root configured, write packages with:

```bash
python -m event_sonification_workbench.cli mot17-package \
  --sequence MOT17-02-DPM \
  --output-directory outputs

python -m event_sonification_workbench.cli kitti-package \
  --sequence 0000 \
  --output-directory outputs
```

Each command parses the selected sequence, rejects parser errors, runs Issue #4 collection
validation and writes only a valid package. Its console summary contains the run ID, event count,
filenames and hashes but no local directory path.

## Schema decision

The writer found no defect in common schema `0.2.0`. File layout, CSV encoding, run provenance and
collection ordering are output-format concerns rather than event-record fields, so the common schema
remains unchanged.
