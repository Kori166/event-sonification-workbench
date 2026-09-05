# Synthetic Audio-Rendering Fixture

The `cues.json` fixture is a manually created, non-dataset cue collection designed to test various audio scenarios, including centre, hard-left, and hard-right panning, varying amplitudes and frequencies, overlapping sounds, fractional sample rounding, and non-zero attack/release envelopes.

To ensure independent verification, `expected.json` records hand-calculated baseline values based on renderer policy version `0.1.0`, meaning tests do not rely on the renderer under test to generate the expected results.

Additionally, the fixture contains no audio files or private paths. During runtime, tests pass these records through the existing Milestone 1 cue-package writer and generate WAV output files exclusively inside pytest temporary directories.