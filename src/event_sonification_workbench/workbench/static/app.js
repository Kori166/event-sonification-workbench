/*
  Purpose:
  JavaScript for the read-only workbench interface.

  This file loads retained sonification sessions and synchronises the
  source frames, event overlays, generated audio, timeline, technical
  metrics and cue-level provenance information.

  The interface does not generate research results. It displays outputs
  already produced and retained by the processing and evaluation pipeline.


  Technical References and Provenance:

  MDN Web Docs (no date) 'Fetch API' [online]. Available from:
  https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API

  Used for:
  - requesting session metadata
  - loading frame records
  - loading timeline windows
  - loading technical evaluation results
  - retrieving cue provenance records


  MDN Web Docs (no date) 'URL' [online]. Available from:
  https://developer.mozilla.org/en-US/docs/Web/API/URL

  Used for:
  - constructing API request URLs
  - adding the selected session_id query parameter without manual
    string concatenation


  MDN Web Docs (no date) 'HTMLMediaElement' [online]. Available from:
  https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement

  Used for:
  - WAV playback
  - reading and setting the current playback time
  - play and pause controls
  - audio muting
  - synchronising the visual inspection interface with the audio


  MDN Web Docs (no date) 'Window: requestAnimationFrame() method'
  [online]. Available from:
  https://developer.mozilla.org/en-US/docs/Web/API/Window/requestAnimationFrame

  Used for:
  - keeping the playback position, displayed frame, timeline cursor
    and selected evidence synchronised while audio is playing


  MDN Web Docs (no date) 'Canvas API' [online]. Available from:
  https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API

  Used for:
  - drawing the synchronised event, cue and suppression timeline
  - drawing frame boundaries
  - drawing the current playback position
  - highlighting the current frame and selected cue


  MDN Web Docs (no date) 'SVG' [online]. Available from:
  https://developer.mozilla.org/en-US/docs/Web/SVG

  Used for:
  - drawing event bounding boxes over source video frames
  - displaying object class and track labels
  - making represented events selectable from the image overlay


  MDN Web Docs (no date) 'Document.createElementNS()' [online].
  Available from:
  https://developer.mozilla.org/en-US/docs/Web/API/Document/createElementNS

  Used for:
  - creating SVG groups, rectangles and text labels for the
    frame-level event overlay


  MDN Web Docs (no date) 'Image() constructor' [online]. Available from:
  https://developer.mozilla.org/en-US/docs/Web/API/HTMLImageElement/Image

  Used for:
  - preloading upcoming source frames
  - reducing visible delays when stepping through or playing
    consecutive frames


  MDN Web Docs (no date) 'Promise' [online]. Available from:
  https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise

  Used for:
  - asynchronous API requests
  - waiting for source images to load
  - loading independent session components concurrently


  MDN Web Docs (no date) 'Map' [online]. Available from:
  https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Map

  Used for:
  - tracking source-frame image preload operations by frame number


  MDN Web Docs (no date) 'Set' [online]. Available from:
  https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Set

  Used for:
  - recording event identifiers that have already raised an
    evidence-integrity warning
  - preventing the same anomaly from being reported repeatedly


  MDN Web Docs (no date) 'EventTarget.addEventListener()' [online].
  Available from:
  https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/addEventListener

  Used for:
  - playback controls
  - frame stepping
  - timeline interaction
  - cue selection
  - session selection
  - keyboard controls
  - responsive timeline resizing


  MDN Web Docs (no date) 'KeyboardEvent' [online]. Available from:
  https://developer.mozilla.org/en-US/docs/Web/API/KeyboardEvent

  Used for:
  - Space-bar play/pause control
  - left/right frame navigation
  - keyboard activation of selectable event overlays

  Project-Specific Implementation:
  The session state model, timeline-window logic, event/cue/suppression
  display, cue trace structure, dataset-specific labels, technical metric
  selection and evidence-integrity behaviour are specific to this MSc
  project and its retained API outputs.

  AI Assistance:
  Generative AI was used during development to support code review,
  debugging and refactoring. Suggested changes were reviewed thoroughly
  prior to use.
*/

"use strict";
const $ = (selector) => document.querySelector(selector);

const audio = $("#audio");
const seek = $("#seek");
const currentTimeDisplay = $("#currentTime");
const playPause = $("#playPause");
const sessionSelect = $("#sessionSelect");
const timelineCanvas = $("#timeline");
const timelineContext = timelineCanvas.getContext("2d");
const timelineBaseCanvas = document.createElement("canvas");
const timelineBaseContext = timelineBaseCanvas.getContext("2d");
const overlay = $("#eventOverlay");

const TIMELINE_HEIGHT = 198;
const TIMELINE_EDGE_MARGIN_SECONDS = 0.25;
const CUE_HIT_RADIUS_PX = 7;
const SVG_NS = "http://www.w3.org/2000/svg";

const state = {
  sessionId: null,
  generation: 0,
  session: null,
  frame: null,
  frameNumber: -1,
  frameContext: null,
  framePending: false,
  frameRequest: 0,
  timeline: null,
  timelinePending: false,
  timelineRequest: 0,
  selectedCue: null,
  selectedCueFrame: null,
  selectedCueTime: null,
  traceRequest: 0,
  integrityAnomalies: new Set(),
  lastPlaybackTime: null,
  preloadImages: new Map(),
};

// General Helpers

function notice(message) {
  const element = $("#notice");
  element.textContent = message;
  element.classList.add("show");
  setTimeout(() => element.classList.remove("show"), 4000);
}

function withSession(path, sessionId = state.sessionId) {
  if (!sessionId) return path;
  const url = new URL(path, location.origin);
  url.searchParams.set("session_id", sessionId);
  return `${url.pathname}${url.search}`;
}

async function getJson(path, sessionId = state.sessionId) {
  const response = await fetch(withSession(path, sessionId), {
    headers: { Accept: "application/json" },
  });
  const body = await response.json();
  if (!response.ok) {
    throw new Error(body.error?.code || "request_failed");
  }
  return body;
}

function datasetName(dataset) {
  return dataset === "kitti_tracking" ? "KITTI Tracking" : "MOT17";
}

function formatTime(seconds) {
  const safe = Number.isFinite(seconds) ? Math.max(0, seconds) : 0;
  const minutes = Math.floor(safe / 60).toString().padStart(2, "0");
  const remainder = (safe % 60).toFixed(3).padStart(6, "0");
  return `${minutes}:${remainder}`;
}

function formatPercent(value) {
  return `${(value * 100).toFixed(2)}%`;
}

function formatNumber(value, digits = 2) {
  return Number(value).toLocaleString(undefined, { maximumFractionDigits: digits });
}

function escapeHtml(value) {
  const replacements = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;",
  };
  return String(value).replace(/[&<>"']/g, char => replacements[char]);
}

function updateTransport(seconds) {
  seek.value = seconds;
  currentTimeDisplay.textContent = formatTime(seconds);
}

// Session And Evaluation

function renderSession(summary) {
  $("#sequenceTitle").textContent = `${datasetName(summary.dataset)} · ${summary.sequence}`;
  seek.max = summary.timing.audio_duration_seconds;
  $("#duration").textContent = formatTime(summary.timing.audio_duration_seconds);
  const rows = [
    ["Session ID", summary.session_id],
    ["Evidence", `${summary.counts.events.toLocaleString()} events · ${summary.counts.cues.toLocaleString()} cues`],
    ["Suppressions", summary.counts.suppressions.toLocaleString()],
    ["Media Timing", `${summary.counts.frames} frames @ ${summary.timing.frame_rate} fps`],
    ["Audio", `${formatTime(summary.timing.audio_duration_seconds)} · ${summary.timing.sample_rate_hz.toLocaleString()} Hz`],
    ["WAV SHA-256", summary.audio.sha256],
  ];
  $("#sessionDetails").innerHTML = rows
    .map(([name, value]) => `<div><dt>${escapeHtml(name)}</dt><dd>${escapeHtml(value)}</dd></div>`)
    .join("");
}

async function renderEvaluation(generation = state.generation) {
  const report = await getJson("/api/evaluation");
  if (generation !== state.generation) return;
  const grid = $("#metricGrid");
  if (!report.available) {
    grid.innerHTML = '<div class="trace-empty">No technical evaluation report is available for this session.</div>';
    return;
  }
  const metrics = report.metrics;
  const cards = [
    ["Eligible Event Coverage", formatPercent(metrics.event_coverage.eligible_event_coverage.value)],
    ["Source Representation", formatPercent(metrics.event_coverage.source_representation_rate.value)],
    ["Cue Density / Second", formatNumber(metrics.cue_density.cues_per_second)],
    ["Peak Concurrency", formatNumber(metrics.overlap_burden.peak_concurrency, 0)],
    ["Suppression Rate", formatPercent(metrics.event_coverage.suppression_rate.value)],
    ["Fully Traceable Cues", formatPercent(metrics.traceability.fully_traceable_cue.value)],
  ];
  grid.innerHTML = cards
    .map(([label, value]) => `<div class="metric"><span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong></div>`)
    .join("");
}

// Event Overlay

function reportIntegrityAnomaly(eventId) {
  if (state.integrityAnomalies.has(eventId)) return;
  state.integrityAnomalies.add(eventId);
  const warning = $("#integrityWarning");
  warning.textContent = "Evidence-integrity warning: an event has no retained cue or suppression outcome.";
  warning.hidden = false;
  console.error("evidence_integrity_anomaly:unresolved_stage_2_outcome");
}

function outcomeFor(event) {
  const outcome = event.stage_2_outcome?.status;
  if (outcome === "represented" || outcome === "suppressed") {
    return outcome;
  }
  reportIntegrityAnomaly(event.event_id);
  return "anomaly";
}

function renderOverlay(frame) {
  overlay.setAttribute("viewBox", `0 0 ${frame.image.width} ${frame.image.height}`);
  overlay.replaceChildren();
  for (const event of frame.events) {
    const outcome = outcomeFor(event);
    const group = document.createElementNS(SVG_NS, "g");
    const rectangle = document.createElementNS(SVG_NS, "rect");
    rectangle.setAttribute("x", event.bbox.x);
    rectangle.setAttribute("y", event.bbox.y);
    rectangle.setAttribute("width", event.bbox.width);
    rectangle.setAttribute("height", event.bbox.height);
    rectangle.setAttribute("class", `event-box ${outcome}`);
    const label = document.createElementNS(SVG_NS, "text");
    label.setAttribute("x", event.bbox.x + 3);
    label.setAttribute("y", Math.max(22, event.bbox.y - 7));
    label.setAttribute("class", "event-label");
    label.textContent = `${event.object_class} · t${event.track_id}`;
    const cueId = outcome === "represented" ? event.stage_2_outcome?.cue_id : null;
    if (cueId) {
      group.setAttribute("class", "event-cue-control");
      group.setAttribute("role", "button");
      group.setAttribute("tabindex", "0");
      group.setAttribute("focusable", "true");
      group.setAttribute("data-cue-id", cueId);
      group.setAttribute(
        "aria-label",
        `Select ${event.object_class} track ${event.track_id} cue at frame ${event.frame}`,
      );
      const select = () => selectCue(cueId).catch(error => notice(error.message));
      group.addEventListener("click", select);
      group.addEventListener("keydown", event => {
        if (event.key !== "Enter" && event.key !== " ") return;
        event.preventDefault();
        event.stopPropagation();
        select();
      });
    }
    group.append(rectangle, label);
    overlay.append(group);
  }
  updateCueSelection();
}

// Frames

function setFrameContext(context) {
  if (context === state.frameContext) return;
  state.frameContext = context;
  $("#frameKind").textContent = context === "cue" ? "Current Frame" : "Playback Frame";
}

async function loadFrame(frameNumber, context = "playback") {
  setFrameContext(context);
  if (frameNumber === state.frameNumber) return;
  const generation = state.generation;
  const requestId = ++state.frameRequest;
  state.framePending = true;
  try {
    const frame = await getJson(`/api/frames/${frameNumber}`);
    if (generation !== state.generation || requestId !== state.frameRequest) return;
    const imageUrl = withSession(frame.image_url);
    await prepareFrameImage(frame.frame, imageUrl);
    if (generation !== state.generation || requestId !== state.frameRequest) return;
    state.frame = frame;
    state.frameNumber = frameNumber;
    const image = $("#sourceImage");
    image.onload = () => {
      if (generation === state.generation) {
        $("#viewerLoading").hidden = true;
      }
    };
    image.src = imageUrl;
    preloadFollowingFrames(frame.frame, generation);
    $("#frameNumber").textContent = String(frame.frame).padStart(3, "0");
    $("#frameTime").textContent = `${frame.timestamp_seconds.toFixed(3)} s`;
    renderOverlay(frame);
    renderFrameCues();
  } finally {
    if (requestId === state.frameRequest) {
      state.framePending = false;
    }
  }
}

function prepareFrameImage(frameNumber, imageUrl) {
  const existing = state.preloadImages.get(frameNumber);
  if (existing) return existing;
  const image = new Image();
  let promise = new Promise((resolve, reject) => {
    image.onload = () => resolve(image);
    image.onerror = () => reject(new Error("frame_image_unavailable"));
  });
  promise = promise.finally(() => {
    if (state.preloadImages.get(frameNumber) === promise) {
      state.preloadImages.delete(frameNumber);
    }
  });
  state.preloadImages.set(frameNumber, promise);
  image.src = imageUrl;
  return promise;
}

function preloadFollowingFrames(frameNumber, generation) {
  if (!state.session || generation !== state.generation) return;
  for (const nextFrame of [frameNumber + 1, frameNumber + 2]) {
    if (nextFrame >= state.session.counts.frames || state.preloadImages.size >= 2) break;
    prepareFrameImage(nextFrame, withSession(`/api/frames/${nextFrame}/image`))
      .catch(() => {});
  }
}

// Timeline Drawing

function resizeTimeline() {
  const ratio = devicePixelRatio || 1;
  const width = Math.max(300, timelineCanvas.clientWidth);
  timelineCanvas.width = Math.floor(width * ratio);
  timelineCanvas.height = Math.floor(TIMELINE_HEIGHT * ratio);
  timelineBaseCanvas.width = Math.floor(width * ratio);
  timelineBaseCanvas.height = Math.floor(TIMELINE_HEIGHT * ratio);
  timelineContext.setTransform(ratio, 0, 0, ratio, 0, 0);
  timelineBaseContext.setTransform(ratio, 0, 0, ratio, 0, 0);
  rebuildTimelineBase();
  drawTimeline();
}

function timelineX(timestamp, width) {
  const { start_seconds: start, end_seconds: end } = state.timeline.window;
  return ((timestamp - start) / (end - start)) * width;
}

function frameForTime(timestamp, frameRate, frameCount) {
  return Math.min(
    Math.floor(Math.max(0, timestamp) * frameRate),
    frameCount - 1,
  );
}

function cueInspectionIsAligned() {
  return (
    state.selectedCueFrame !== null &&
    state.selectedCueTime !== null &&
    audio.paused &&
    Math.abs(audio.currentTime - state.selectedCueTime) <= 1e-6
  );
}

function drawCurrentFrameInterval(height, width) {
  if (!state.session || !state.timeline) return;
  const frameRate = state.session.timing.frame_rate;
  const { start_seconds: windowStart, end_seconds: windowEnd } = state.timeline.window;
  const frame = cueInspectionIsAligned()
    ? state.selectedCueFrame
    : frameForTime(audio.currentTime, frameRate, state.session.counts.frames);
  const highlightStart = Math.max(windowStart, frame / frameRate);
  const highlightEnd = Math.min(windowEnd, (frame + 1) / frameRate);
  if (highlightEnd <= highlightStart) return;
  const x = timelineX(highlightStart, width);
  const endX = timelineX(highlightEnd, width);
  timelineContext.fillStyle = "rgba(117, 240, 193, 0.09)";
  timelineContext.fillRect(x, 0, endX - x, height);
}

function drawFrameBoundaries(context, height, width) {
  if (!state.session || !state.timeline) return;
  const frameRate = state.session.timing.frame_rate;
  const { start_seconds: start, end_seconds: end } = state.timeline.window;
  const firstFrame = Math.ceil(start * frameRate);
  const lastFrame = Math.floor(end * frameRate);
  const pixelsPerFrame = width / ((end - start) * frameRate);
  context.strokeStyle = "rgba(140, 163, 157, 0.18)";
  context.fillStyle = "rgba(140, 163, 157, 0.72)";
  context.lineWidth = 1;
  context.font = "9px ui-monospace, monospace";
  for (let frame = firstFrame; frame <= lastFrame; frame++) {
    const time = frame / frameRate;
    if (time < start || time > end) continue;
    const x = timelineX(time, width);
    context.beginPath();
    context.moveTo(x, 0);
    context.lineTo(x, height);
    context.stroke();
    if (pixelsPerFrame >= 32 && x <= width - 18) {
      context.fillText(`f${frame}`, x + 3, 10);
    }
  }
}

function drawMarkers(context, items, lane, color, timestampField, height, width) {
  const laneHeight = height / 3;
  const y = lane * laneHeight;
  context.fillStyle = color;
  for (const item of items) {
    const x = timelineX(item[timestampField], width);
    context.fillRect(Math.max(0, x - 0.65), y + 12, 1.3, laneHeight - 24);
  }
}

function rebuildTimelineBase() {
  const width = timelineCanvas.clientWidth;
  timelineBaseContext.clearRect(0, 0, width, TIMELINE_HEIGHT);
  timelineBaseContext.strokeStyle = "#172c28";
  timelineBaseContext.lineWidth = 1;
  for (let lane = 1; lane < 3; lane++) {
    const y = lane * (TIMELINE_HEIGHT / 3);
    timelineBaseContext.beginPath();
    timelineBaseContext.moveTo(0, y);
    timelineBaseContext.lineTo(width, y);
    timelineBaseContext.stroke();
  }
  if (!state.timeline) return;
  drawFrameBoundaries(timelineBaseContext, TIMELINE_HEIGHT, width);
  drawMarkers(timelineBaseContext, state.timeline.events, 0, "#65b8ff", "timestamp_seconds", TIMELINE_HEIGHT, width);
  drawMarkers(timelineBaseContext, state.timeline.cues, 1, "#75f0c1", "start_time_seconds", TIMELINE_HEIGHT, width);
  drawMarkers(timelineBaseContext, state.timeline.suppressions, 2, "#ff718d", "timestamp_seconds", TIMELINE_HEIGHT, width);
}

function drawTimeline() {
  const width = timelineCanvas.clientWidth;
  timelineContext.clearRect(0, 0, width, TIMELINE_HEIGHT);
  timelineContext.fillStyle = "#07110f";
  timelineContext.fillRect(0, 0, width, TIMELINE_HEIGHT);
  if (!state.timeline) return;
  drawCurrentFrameInterval(TIMELINE_HEIGHT, width);
  timelineContext.drawImage(
    timelineBaseCanvas,
    0,
    0,
    timelineBaseCanvas.width,
    timelineBaseCanvas.height,
    0,
    0,
    width,
    TIMELINE_HEIGHT,
  );
  const selected = state.timeline.cues.find(cue => cue.cue_id === state.selectedCue);
  if (selected) {
    const x = timelineX(selected.start_time_seconds, width);
    timelineContext.strokeStyle = "#fff";
    timelineContext.lineWidth = 2;
    timelineContext.strokeRect(x - 3.5, 76, 7, 46);
  }
  const cursor = timelineX(audio.currentTime, width);
  timelineContext.strokeStyle = "#fff";
  timelineContext.lineWidth = 1.5;
  timelineContext.beginPath();
  timelineContext.moveTo(cursor, 0);
  timelineContext.lineTo(cursor, TIMELINE_HEIGHT);
  timelineContext.stroke();
  timelineContext.fillStyle = "#fff";
  timelineContext.beginPath();
  timelineContext.moveTo(cursor - 4, 0);
  timelineContext.lineTo(cursor + 4, 0);
  timelineContext.lineTo(cursor, 6);
  timelineContext.fill();
}

function cueAtCanvasPoint(event) {
  if (!state.timeline) return null;
  const bounds = timelineCanvas.getBoundingClientRect();
  const x = event.clientX - bounds.left;
  const y = event.clientY - bounds.top;
  const laneHeight = bounds.height / 3;
  if (y < laneHeight + 8 || y > 2 * laneHeight - 8) return null;
  let closest = null;
  let closestDistance = CUE_HIT_RADIUS_PX + 1;
  for (const cue of state.timeline.cues) {
    const distance = Math.abs(
      timelineX(cue.start_time_seconds, bounds.width) - x,
    );
    if (distance <= CUE_HIT_RADIUS_PX && distance < closestDistance) {
      closest = cue;
      closestDistance = distance;
    }
  }
  return closest;
}

// Frame Cues

function compareCueOrder(a, b) {
  const timeDifference = a.start_time_seconds - b.start_time_seconds;
  if (timeDifference) return timeDifference;
  const trackDifference = String(a.track_id).localeCompare(
    String(b.track_id),
    undefined,
    { numeric: true },
  );
  return trackDifference || a.cue_id.localeCompare(b.cue_id);
}

function renderFrameCues() {
  const container = $("#frameCues");
  const cues = [...(state.frame?.cues || [])].sort(compareCueOrder);
  const frameNumber = state.frame?.frame;
  $("#frameCueSummary").textContent = Number.isInteger(frameNumber)
    ? `Frame ${String(frameNumber).padStart(3, "0")} · ${cues.length} ${cues.length === 1 ? "cue" : "cues"}`
    : "—";
  container.replaceChildren();
  if (!cues.length) {
    const empty = document.createElement("p");
    empty.className = "cue-empty";
    empty.textContent = `No generated cues on frame ${String(frameNumber).padStart(3, "0")}.`;
    container.append(empty);
    return;
  }
  for (const cue of cues) {
    const button = document.createElement("button");
    const active = state.selectedCue === cue.cue_id;
    button.type = "button";
    button.className = `cue-chip${active ? " active" : ""}`;
    button.setAttribute("aria-pressed", String(active));
    button.textContent = `${cue.start_time_seconds.toFixed(3)}s · ${cue.object_class} · t${cue.track_id}`;
    button.title = cue.cue_id;
    button.addEventListener("click", () => {
      selectCue(cue.cue_id).catch(error => notice(error.message));
    });
    container.append(button);
  }
}

// Timeline Loading

function cachedTimelineCovers(time) {
  if (!state.timeline || !state.session) return false;
  const { start_seconds: start, end_seconds: end } = state.timeline.window;
  const duration = state.session.timing.audio_duration_seconds;
  const lower = start <= 0 ? start : start + TIMELINE_EDGE_MARGIN_SECONDS;
  const upper = end >= duration ? end : end - TIMELINE_EDGE_MARGIN_SECONDS;
  return time >= lower && time <= upper;
}

function timelineWindowFor(time) {
  const duration = state.session.timing.audio_duration_seconds;
  let start = Math.max(0, time - 0.35);
  let end = Math.min(duration, start + 1);
  start = Math.max(0, end - 1);
  return { start, end };
}

async function loadTimeline(force = false) {
  if (!state.session) return;
  const generation = state.generation;
  const time = audio.currentTime;
  if (!force && cachedTimelineCovers(time)) return;
  if (!force && state.timelinePending) return;
  const { start, end } = timelineWindowFor(time);
  const requestId = ++state.timelineRequest;
  state.timelinePending = true;
  try {
    const timeline = await getJson(
      `/api/timeline?start=${start.toFixed(6)}&end=${end.toFixed(6)}`,
    );
    if (generation !== state.generation || requestId !== state.timelineRequest) return;
    state.timeline = timeline;
    $("#windowLabel").textContent =
      `${timeline.window.start_seconds.toFixed(3)}–${timeline.window.end_seconds.toFixed(3)} s`;
    rebuildTimelineBase();
  } finally {
    if (requestId === state.timelineRequest) {
      state.timelinePending = false;
    }
  }
}

// Cue Selection And Provenance

function updateCueSelection() {
  for (const button of document.querySelectorAll("#frameCues .cue-chip")) {
    const active = button.title === state.selectedCue;
    button.classList.toggle("active", active);
    button.setAttribute("aria-pressed", String(active));
  }
  for (const control of overlay.querySelectorAll(".event-cue-control")) {
    const active = control.dataset.cueId === state.selectedCue;
    control.classList.toggle("selected", active);
    control.setAttribute("aria-pressed", String(active));
  }
}

function traceNode(title, lines) {
  const content = lines
    .map(([label, value]) => `<p>${escapeHtml(label)}<br><strong>${escapeHtml(value)}</strong></p>`)
    .join("");
  return `<section class="trace-node"><h3>${escapeHtml(title)}</h3>${content}</section>`;
}

function renderTrace(trace) {  
  const shortCue = trace.cue.cue_id.replace("cue:", "").slice(0, 12);
  const shortEvent = trace.event.event_id.split(":").slice(-3).join(":");
  const content = $("#traceContent");
  content.className = "trace-chain";
  content.innerHTML = [
    traceNode("Cue", [
      ["ID", shortCue],
      ["Start (Event Timestamp)", `${trace.cue.start_time_seconds.toFixed(6)} s`],
      ["Frequency (Vertical Centre)", `${trace.cue.frequency_hz.toFixed(1)} Hz`],
      ["Stereo Pan (Horizontal Centre)", trace.cue.stereo_pan],
      ["Amplitude (Box Area)", trace.cue.amplitude],
      ["Duration", `${trace.cue.duration_seconds.toFixed(3)} s`],
    ]),
    traceNode("Event", [
      ["ID", shortEvent],
      ["Source Frame / Track", `${trace.event.frame} / ${trace.event.track_id}`],
      ["Class", trace.event.object_class],
    ]),
    traceNode("Annotation", [
      ["Logical Source", trace.source_annotation.logical_path],
      ["Physical Row", trace.source_annotation.row],
    ]),
    traceNode("Configuration", [
      ["Preset", `${trace.configuration.preset.name} ${trace.configuration.preset.version}`],
      ["Renderer", `${trace.configuration.renderer.name} ${trace.configuration.renderer.version}`],
      ["Class Modifier", "Recorded for traceability. Not applied to waveform."],
    ]),
    traceNode("Render", [
      ["Samples", `${trace.render.start_sample}–${trace.render.end_sample_exclusive}`],
      ["Duration", `${trace.render.duration_samples} @ ${trace.render.sample_rate_hz} Hz`],
    ]),
  ].join("");
  updateCueSelection();
  drawTimeline();
}

async function selectCue(cueId) {
  const generation = state.generation;
  const requestId = ++state.traceRequest;
  const cueInWindow =
    state.timeline?.cues.some(cue => cue.cue_id === cueId) ?? false;
  const trace = await getJson(
    `/api/trace?cue_id=${encodeURIComponent(cueId)}`,
  );
  if (generation !== state.generation || requestId !== state.traceRequest) return;
  audio.pause();
  audio.currentTime = trace.cue.start_time_seconds;
  state.lastPlaybackTime = audio.currentTime;
  state.selectedCue = cueId;
  state.selectedCueFrame = trace.event.frame;
  state.selectedCueTime = trace.cue.start_time_seconds;
  updateTransport(audio.currentTime);
  drawTimeline();
  await loadFrame(trace.event.frame, "cue");
  if (generation !== state.generation || requestId !== state.traceRequest) return;
  if (!cueInWindow) {
    await loadTimeline(true);
    if (generation !== state.generation || requestId !== state.traceRequest) return;
  }
  renderTrace(trace);
}

// Playback

function clearCueFrameAlignment() {
  state.selectedCueFrame = null;
  state.selectedCueTime = null;
  setFrameContext("playback");
}

function setAudioTime(value) {
  const duration =
    state.session?.timing.audio_duration_seconds ||
    audio.duration ||
    0;
  clearCueFrameAlignment();
  audio.currentTime = Math.min(Math.max(value, 0), duration);
  updateTransport(audio.currentTime);
  loadTimeline().catch(error => notice(error.message));
}

function stepFrame(direction) {
  if (!state.session) return;
  audio.pause();
  const frameDuration = 1 / state.session.timing.frame_rate;
  setAudioTime(audio.currentTime + direction * frameDuration);
}

// Session Switching

function resetSessionState(sessionId) {
  state.generation++;
  state.sessionId = sessionId;
  state.session = null;
  state.frame = null;
  state.frameNumber = -1;
  state.frameContext = null;
  state.framePending = false;
  state.timeline = null;
  state.timelinePending = false;
  state.selectedCue = null;
  state.selectedCueFrame = null;
  state.selectedCueTime = null;
  state.traceRequest++;
  state.frameRequest++;
  state.timelineRequest++;
  state.integrityAnomalies.clear();
  state.lastPlaybackTime = null;
  state.preloadImages.clear();
  audio.pause();
  audio.removeAttribute("src");
  audio.load();
  seek.max = 1;
  updateTransport(0);
  playPause.textContent = "▶";
  playPause.setAttribute("aria-label", "Play");
  $("#duration").textContent = "00:00.000";
  $("#sequenceTitle").textContent = "Loading…";
  $("#frameKind").textContent = "Playback Frame";
  $("#frameNumber").textContent = "—";
  $("#frameTime").textContent = "—";
  $("#windowLabel").textContent = "—";
  const warning = $("#integrityWarning");
  warning.textContent = "";
  warning.hidden = true;
  const image = $("#sourceImage");
  image.onload = null;
  image.removeAttribute("src");
  $("#viewerLoading").hidden = false;
  overlay.replaceChildren();
  $("#frameCueSummary").textContent = "—";
  $("#frameCues").replaceChildren();
  $("#sessionDetails").replaceChildren();
  $("#metricGrid").innerHTML =
    '<div class="skeleton"></div>'.repeat(4);
  const traceState = $("#traceState");
  traceState.textContent = "Select A Cue";
  traceState.className = "evidence-tag neutral";
  const traceContent = $("#traceContent");
  traceContent.className = "trace-empty";
  traceContent.textContent =
    "Choose a cue marker or frame cue to inspect its source and rendered sample.";
  const noticeElement = $("#notice");
  noticeElement.textContent = "";
  noticeElement.classList.remove("show");
  rebuildTimelineBase();
  drawTimeline();
}

async function switchSession(sessionId) {
  resetSessionState(sessionId);
  const generation = state.generation;
  sessionSelect.value = sessionId;
  const summary = await getJson("/api/session", sessionId);
  if (generation !== state.generation) return;
  state.session = summary;
  renderSession(summary);
  audio.src = withSession("/api/audio", sessionId);
  audio.load();
  await Promise.all([
    renderEvaluation(generation),
    loadFrame(0),
    loadTimeline(true),
  ]);
  if (generation === state.generation) {
    resizeTimeline();
  }
}

// Synchronisation Loop

function tick() {
  if (state.session) {
    const time = audio.currentTime;
    if (time !== state.lastPlaybackTime) {
      state.lastPlaybackTime = time;
      updateTransport(time);
      const inspectingCue = cueInspectionIsAligned();
      const frame = inspectingCue
        ? state.selectedCueFrame
        : frameForTime(
            time,
            state.session.timing.frame_rate,
            state.session.counts.frames,
          );
      if (frame !== state.frameNumber && !state.framePending) {
        loadFrame(frame, inspectingCue ? "cue" : "playback")
          .catch(error => notice(error.message));
      }
      loadTimeline().catch(error => notice(error.message));
      drawTimeline();
    }
  }
  requestAnimationFrame(tick);
}

// Controls
playPause.addEventListener("click", async () => {
  if (!state.session) return;
  if (audio.paused) {
    await audio.play();
  } else {
    audio.pause();
  }
});
audio.addEventListener("play", () => {
  clearCueFrameAlignment();
  playPause.textContent = "❚❚";
  playPause.setAttribute("aria-label", "Pause");
});
audio.addEventListener("pause", () => {
  playPause.textContent = "▶";
  playPause.setAttribute("aria-label", "Play");
});
seek.addEventListener("input", () => {
  setAudioTime(Number(seek.value));
});
$("#stepBack").addEventListener("click", () => stepFrame(-1));
$("#stepForward").addEventListener("click", () => stepFrame(1));
$("#mute").addEventListener("click", event => {
  audio.muted = !audio.muted;
  event.currentTarget.textContent = audio.muted ? "Muted" : "Audio on";
});
timelineCanvas.addEventListener("click", event => {
  const cue = cueAtCanvasPoint(event);
  if (cue) {
    selectCue(cue.cue_id).catch(error => notice(error.message));
  }
});
timelineCanvas.addEventListener("mousemove", event => {
  timelineCanvas.style.cursor =
    cueAtCanvasPoint(event) ? "pointer" : "default";
});
timelineCanvas.addEventListener("mouseleave", () => {
  timelineCanvas.style.cursor = "default";
});
window.addEventListener("resize", resizeTimeline);
window.addEventListener("keydown", event => {
  if (
    event.target instanceof HTMLInputElement ||
    event.target instanceof HTMLSelectElement
  ) {
    return;
  }
  if (event.code === "Space") {
    event.preventDefault();
    playPause.click();
  }
  if (event.code === "ArrowLeft") {
    event.preventDefault();
    $("#stepBack").click();
  }
  if (event.code === "ArrowRight") {
    event.preventDefault();
    $("#stepForward").click();
  }
});

// Initialisation

async function initialise() {
  try {
    const catalogue = await getJson("/api/sessions", null);
    sessionSelect.replaceChildren();
    for (const session of catalogue.sessions) {
      const option = document.createElement("option");
      option.value = session.session_id;
      option.textContent =
        `${datasetName(session.dataset)} · ${session.sequence}`;
      sessionSelect.append(option);
    }
    sessionSelect.disabled = false;
    sessionSelect.addEventListener("change", () => {
      switchSession(sessionSelect.value).catch(error => {
        $("#sequenceTitle").textContent = "Session unavailable";
        notice(error.message);
      });
    });
    await switchSession(catalogue.default_session_id);
    requestAnimationFrame(tick);
  } catch (error) {
    $("#sequenceTitle").textContent = "Session unavailable";
    notice(error.message);
  }
}
initialise();
