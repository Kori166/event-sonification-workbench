# Collection Validation Fixtures

`collection_cases.json` defines deterministic event collections for Issue #4 without copying a
second set of normalised records. The valid MOT17 and KITTI Tracking collections are the complete
12-row outputs of the already committed adapter fixtures. Their listed indexes make the selection
and order explicit.

Invalid collections are declarative transformations of fresh deep copies of those parsed events.
The supported test-only operations are `remove`, `set` and `append_duplicate`. They cover a missing
required field, an incorrect type, a duplicate identifier, an invalid timestamp, an invalid box and
multiple errors in one collection. The tests assert that every named case is applied as declared.

These transformation records are project-authored synthetic data. Dataset attribution and licence
information remain with the reused source fixtures:

- `tests/fixtures/mot17/README.md`
- `tests/fixtures/kitti/README.md`

No private path, image, video, audio or additional dataset-derived annotation is included here.
