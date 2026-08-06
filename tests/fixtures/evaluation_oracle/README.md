# Evaluation Oracle Fixture

This entirely synthetic fixture freezes the Stage 3 Milestone 1 method before real-data use.
`oracle-calculation.md` is the primary manual derivation. `input.json` is the internally consistent
record chain, and `faults.json` specifies named deterministic mutations for negative tests. The
manifest records exact hashes of those reviewed files and the small synthetic source CSV.

The fixture is project-authored and contains no MOT17, KITTI, private path or media content. The
repeated package/configuration hash strings inside `input.json` are deliberate test identities;
only the SHA-256 values in `manifest.json` claim exact physical fixture-file identity.
