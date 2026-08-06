# Manually Calculated Technical-Evaluation Oracle

## Construction

This fixture is synthetic and has no MOT17, KITTI or private-data dependency. The sample rate is
10 Hz and the rendered timeline is `[0,30)` samples, or `[0,3)` seconds. The physical source CSV
hash is `d923541748ae03bab1e2bad768ae80b790bfec16d10faae6a7fdea1ef3a0eb97`.
Repeated digits in package/configuration hashes are deliberate inspectable fixture identities, not
hashes claimed for physical dataset packages. Metric values below were calculated before
implementing the evaluator.

## Event outcomes

| Event | Time (s) | Decision | Cue(s) or record |
|---|---:|---|---|
| event 1 | 0.00 | eligible, represented | cue 1 and cue 2 |
| event 2 | 1.00 | eligible, represented | cue 3 |
| event 3 | 1.50 | intentionally suppressed | `oracle_excluded` |
| event 4 | 2.00 | eligible, represented | cue 4 |
| event 5 | 2.25 | eligible, represented | cue 5 |

There are five valid events, four eligible events, four unique represented events, one suppressed
event and no misses. Therefore:

- eligible coverage = `4/4 = 1`;
- source representation = `4/5 = 0.8`;
- suppression = `1/5 = 0.2`;
- accounting completeness = `5/5 = 1`; and
- missed eligible = `0/4 = 0`.

The fault `eligible_missed_event` removes cue 5 and its render entry. Its expected eligible
coverage is `3/4 = 0.75`, accounting completeness is `4/5 = 0.8`, and missed eligible is
`1/4 = 0.25`. The suppression count remains one.

## Cue and render intervals

| Cue | Event | Scheduled interval (s) | Rendered interval (samples) | Notes |
|---|---|---|---|---|
| 1 | event 1 | `[0.0,1.0)` | `[0,10)` | exact sample boundary |
| 2 | event 1 | `[0.5,1.5)` | `[5,15)` | second cue for one event |
| 3 | event 2 | `[1.0,2.0)` | `[10,20)` | cue 1 ends as cue 3 starts |
| 4 | event 4 | `[2.0,2.5)` | `[20,25)` | cue 3 touches, not overlaps |
| 5 | event 5 | `[2.25,2.75)` | `[23,28)` | `2.25*10=22.5`, half-up to 23 |

Scheduling errors in seconds are `[0,0.5,0,0,0]`; in rounded samples they are `[0,5,0,0,0]`.
Their summaries are count 5, min 0, max 0.5/5, mean 0.1/1, median 0 and p95 0.5/5.

Render-placement errors in seconds are `[0,0,0,0,0.05]`: cue 5 is physically at 2.3 s after
correct half-up quantisation. Integer placement errors are all zero because every rendered start
equals the correctly rounded scheduled start. Seconds summary: count 5, min 0, max 0.05, mean
0.01, median 0, p95 0.05. Sample summary: count 5 and every statistic 0.

End-to-end errors in seconds are `[0,0.5,0,0,0.05]`, giving count 5, min 0, max 0.5, mean 0.11,
median 0 and p95 0.5. Rounded-sample errors are `[0,5,0,0,0]`, giving count 5, min 0, max 5,
mean 1, median 0 and p95 5. Shifting cue 3's rendered interval by one sample produces one render
placement and end-to-end sample error of 1 and a seconds error of 0.1 for that cue.

## Overlap sweep

| Segment (samples) | Active count | Overlap samples | Excess cue-samples |
|---|---:|---:|---:|
| `[0,5)` | 1 | 0 | 0 |
| `[5,10)` | 2 | 5 | 5 |
| `[10,15)` | 2 | 5 | 5 |
| `[15,20)` | 1 | 0 | 0 |
| `[20,23)` | 1 | 0 | 0 |
| `[23,25)` | 2 | 2 | 2 |
| `[25,28)` | 1 | 0 | 0 |
| `[28,30)` | 0 | 0 | 0 |

At sample 10 cue 1 ends while cue 3 starts. Grouping the boundary preserves concurrency two from
10 to 15 rather than creating a spurious concurrency-three instant. At sample 20 cue 3 ends as cue
4 starts, so they do not overlap. Peak concurrency is 2. Overlap is 12 samples / 10 = 1.2 seconds.
Excess concurrency is also 12 cue-samples / 10 = 1.2 cue-seconds. Both normalised measures are
`1.2/3 = 0.4`.

## Density and traceability

Five cues over three seconds give `5/3 = 1.6666666666666667` cues/s and 100 cues/min. Four unique
represented events give `4/3 = 1.3333333333333333` represented events/s. Half-open windows at cue
starts contain at most two starts: `[0,1)` has cues 1 and 2, while the cue at 1 is excluded.

Every cue resolves to the expected event, source file/row, preset, schedule entry, render entry,
cue-package/renderer identity and supplied WAV identity. Each of the four cue traceability rates is
`5/5 = 1`; suppression traceability is `1/1 = 1`; broken-link groups are empty.

The supplied repeat evidence makes semantic, byte, audio and configuration results true. This is a
synthetic same-process test only and is not cross-environment evidence. Empty input has zero counts,
null rates/statistics, zero peak concurrency and no warning. A non-empty zero-duration timeline has
null duration-based rates plus the `zero_duration_timeline` warning.
