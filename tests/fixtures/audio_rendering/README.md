# Synthetic audio-rendering fixture

`cues.json` is a manually authored, non-dataset-derived cue collection. It deliberately covers
centre, hard-left and hard-right pan, different amplitudes/frequencies, overlap, fractional sample
rounding and non-zero attack/release envelopes. `expected.json` records values calculated by hand
from renderer policy `0.1.0`; tests do not derive the oracle with the renderer under test.

The fixture contains no audio or private path. Tests wrap these records in the existing Milestone 1
cue-package writer at runtime and write WAV outputs only below pytest temporary directories.
