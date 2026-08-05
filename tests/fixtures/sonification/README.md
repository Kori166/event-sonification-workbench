# Synthetic cue-scheduling fixture

This fixture is synthetic and carries no third-party dataset rows. It is released under the
repository licence. `source_events.csv` is the human-readable source and its SHA-256 is
`5d6e16eacb6c6c2c4176d837faeab949fd3239f54544a5fff4d83522fbaf29ac`.
The event fixture SHA-256 is
`7e91a37830ece1b5c30f1dd9e77c836ac6321b882a7a133a846a13e8e2808771`.

The five hand-written schema 0.2.0 events exercise two scheduled cues, excluded-class
suppression, minimum-confidence suppression and explicit `dont_care` suppression. Geometry spans
left/right, top/bottom and different areas. `events.json` was manually derived from the CSV using
a 1000 by 1000 image and 25 fps.

`expected_cues.json` applies the documented baseline formulas by hand. For example, the first
frequency is `1760 - 0.25 * (1760 - 220) = 1375 Hz`, pan is
`-1 + 0.25 * (1 - -1) = -0.5`, and amplitude is `0.1 + 0.1 * (0.8 - 0.1) = 0.17`.
Expected cue identifiers were calculated independently from the documented canonical identity,
not produced by the scheduler under test. Expected suppression records are likewise hand-written.
Their SHA-256 values are
`726810a384fde595d74eb6a1b0fabf7f6af31be0b9ec9909a25d1504ee7c36e5` and
`a8f2c011eb998da465e6a0c4e575aa43b9ab7e3df5c8226de8edb2e91167f2fc` respectively.

If the baseline preset changes, this fixture must be reviewed explicitly. A preset change must
not silently regenerate these expected files.
