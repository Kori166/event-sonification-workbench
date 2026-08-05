# Stage 2 Milestone 2: Deterministic WAV Audio Rendering

## Scope completed

Issue #21 adds the configured cue-to-audio vertical slice without changing the Milestone 1 mapper.
It verifies cue-package format `0.1.0`, renders deterministic stereo PCM16 WAV bytes and writes
cue/sample traceability plus renderer/audio provenance. Common event schema `0.2.0`, the baseline
sonification preset and the cue-package structure remain unchanged.

## Configuration and implementation

- Renderer schema/configuration, implementation and rendering-policy versions: `0.1.0`.
- Baseline renderer SHA-256:
  `1c741306f67633543f9f16de557173662005c8c21c4a911fb4bcf8bbde18770b`.
- Renderer schema SHA-256:
  `420fd001904be08b81f33c9c078de9ccce7fb5b4ae93cd07d5bd97dc27d8aea8`.
- Audio: stereo, 44,100 Hz, signed PCM16 little-endian, minimal RIFF/WAVE.
- Synthesis: fixed zero-phase sine, linear attack/release, linear-balance pan and processing order
  `(start_sample, cue_id)`.
- Placement: Decimal round-half-up with exclusive cue ends and at least one sample per positive cue.
- Mixing: ordered sum, master gain, conditional target-peak global gain, then signed full-scale
  half-away-from-zero quantisation and clamping.
- Empty schedule: valid 44-byte zero-frame WAV with complete empty logs/metadata.

`class_modifier` remains trace-only under an explicit renderer policy. This milestone does not
silently give it a new acoustic meaning.

## Fixture evidence

The three-cue manually authored fixture covers centre, hard-left and hard-right pan, different
frequencies/amplitudes and overlap. Fixture SHA-256 is
`3517ee950c8e5bc30fce0587b47aa276c3fc59a7bf24be126e9cbb549ab98254`; its independent oracle hash
is `141389e341612f3243a638122a150dbfb28ab22558cf19425bfbd7d071e73025`.

Manual expectations include start samples `44, 441, 1323`; duration samples `882, 662, 441`;
exclusive ends `926, 1103, 1764`; 1,764 total frames; 44 frames before the first cue; attack 221;
release 441; PCM frame 45 `(37, 37)`; PCM frame 1324 `(0, 96)`; and no peak normalisation.

A disposable actual fixture render produced:

- cue run: `cue-synthetic-audio_fixture-2d0c5c44f2dd15ff`;
- audio run: `audio-synthetic-audio_fixture-903dba6a906b607c`;
- rendered cues: 3; total frames: 1,764;
- WAV SHA-256: `041aa0be80f18ddc770cf0fee1cd4c426509972cc4d386eee72b7b2397081beb`;
- render-log SHA-256: `b0e258ac72664f6d30c22cc7e57165b2351262ce69310ec9d1e6963383c51ba7`;
- renderer-metadata SHA-256:
  `5b266d20d5cff9c5a81cd1f5c5195d4a883ccc9dca3a6e479acde57ec2d332a1`.

The generated package was outside the repository and is not committed.

## Input integrity and traceability

The loader checks exact five-file membership, canonical JSON, metadata hashes, content-derived run
ID, counts, fixed JSON/CSV/log projections, supported mapper/version, event order, unique cue IDs,
source-event IDs, dataset/sequence, preset identity and finite bounded parameters before rendering.
Unsafe or different existing outputs are refused.

The end-to-end committed-fixture test checks annotation-source hash to Stage 1 event package, cue or
suppression record, rendered sample log and WAV hash. Separate fixture tests pass the complete
committed MOT17 and KITTI event collections through the same cue and render contracts.

## Local validation results

Commands were run from the repository root on 5 August 2026:

- `python -m ruff check .`: passed.
- `python -m pytest -m "not integration"`: 178 passed, 2 deselected.
- `python -m pytest`: 178 passed, 2 private-data integration tests skipped clearly.
- Audio-renderer module: 34 tests passed within the final suites.

Skipped private integrations are not reported as passes. This milestone requires committed-fixture
MOT17/KITTI compatibility, not new private full-dataset audio output.

## Problems, limitations and merge gate

- GitHub CLI was unavailable; the connected GitHub capability created and assigned Issue #21.
- Unrelated README, web, launcher and ignore-file work remained present locally and must stay out of
  this milestone's staged scope.
- Floating-point sine/mixing output is byte-repeat tested on the local Windows/Python environment;
  no broader cross-platform identity claim is made before additional evidence exists.
- Synthesis settings are technical choices. Perceptual quality, accessibility, usefulness, safety,
  participant evaluation and Stage 3 metrics are untested and outside scope.
- Generated full-data audio remains ignored. Pull-request CI and review remain merge gates.
