# RQ3 Method Summary

The evaluation contract was fixed before real-data calculation so that outcome categories,
denominators, timing domains, traceability requirements and overlap semantics could not be adjusted
in response to the observed values. Contract `0.1.0` was first checked against a project-authored,
manually calculated synthetic oracle containing represented, multiply represented, intentionally
suppressed and excluded event outcomes plus timing, traceability and interval edge cases.

The real-data cases were MOT17-02-DPM and KITTI Tracking sequence 0000. Before evaluation, the Stage
1 event packages and Stage 2 cue, suppression, render and WAV records were checked for membership,
canonical serialisation, configuration identity, physical hashes and cross-stage links. The cases use
common event schema `0.2.0`, baseline preset `0.1.0` and baseline renderer `0.1.0`.

Event accounting distinguishes represented, intentionally suppressed, explicitly excluded and
missed eligible events. Eligible-event coverage uses eligible events as its denominator; source
representation uses all valid source events. Timing is measured independently for scheduling,
render placement and end-to-end alignment in seconds and samples, with decimal round-half-up sample
placement. Traceability requires resolved event, source-annotation and rendered-sample links and a
resolved suppression record where applicable.

Cue density is calculated over the rendered timeline, and the maximum-start measure uses half-open
one-second windows. Overlap uses half-open render intervals; excess concurrent cue-seconds integrate
concurrency above one, and normalised burden divides that quantity by evaluated duration. Three
isolated reports per dataset were compared semantically and byte-for-byte alongside retained Stage 2
audio/configuration repeat evidence.

The complete contract, input protocol, environment manifest and canonical evidence package retain
the implementation detail and hashes. The evidence boundary is one recorded Windows/AMD64/Python
environment, two selected sequences, one preset and one renderer. No participant evaluation,
perceptual quality measure, accessibility, usability, navigation, mobility or safety outcome was
performed.
