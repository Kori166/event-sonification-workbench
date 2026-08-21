"use strict";

const audio = document.querySelector("#audio");
const seek = document.querySelector("#seek");
const currentTimeDisplay = document.querySelector("#currentTime");
const playPause = document.querySelector("#playPause");
const sessionSelect = document.querySelector("#sessionSelect");
const timelineCanvas = document.querySelector("#timeline");
const timelineContext = timelineCanvas.getContext("2d");
const timelineBaseCanvas = document.createElement("canvas");
const timelineBaseContext = timelineBaseCanvas.getContext("2d");
const overlay = document.querySelector("#eventOverlay");
const TIMELINE_EDGE_MARGIN_SECONDS = 0.25;
const CUE_HIT_RADIUS_PX = 7;
const state = {
  catalogue: null,
  sessionId: null,
  generation: 0,
  session: null,
  frame: null,
  frameNumber: -1,
  frameContext: null,
  framePending: false,
  timeline: null,
  timelinePendingKey: null,
  timelineRequest: 0,
  selectedCue: null,
  selectedCueFrame: null,
  selectedCueTime: null,
  traceRequest: 0,
  frameRequest: 0,
  integrityAnomalies: new Set(),
  lastPlaybackTime: null,
  preloadImages: new Map(),
};

function notice(message) {
  const element = document.querySelector("#notice");
  element.textContent = message;
  element.classList.add("show");
  window.setTimeout(() => element.classList.remove("show"), 4000);
}

function withSession(path, sessionId = state.sessionId) {
  if (!sessionId) return path;
  const url = new URL(path, window.location.origin);
  url.searchParams.set("session_id", sessionId);
  return `${url.pathname}${url.search}`;
}

async function getJson(path, sessionId = state.sessionId) {
  const response = await fetch(withSession(path, sessionId), { headers: { Accept: "application/json" } });
  const body = await response.json();
  if (!response.ok) throw new Error(body.error?.code || "request_failed");
  return body;
}

function formatTime(seconds) {
  const safe = Number.isFinite(seconds) ? Math.max(0, seconds) : 0;
  const minutes = Math.floor(safe / 60).toString().padStart(2, "0");
  const remainder = (safe % 60).toFixed(3).padStart(6, "0");
  return `${minutes}:${remainder}`;
}

function formatPercent(value) { return `${(value * 100).toFixed(2)}%`; }
function formatNumber(value, digits = 2) { return Number(value).toLocaleString(undefined, { maximumFractionDigits: digits }); }
function updateTransportPresentation(seconds) {
  seek.value = seconds;
  currentTimeDisplay.textContent = formatTime(seconds);
}
function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;",
  })[character]);
}

function renderSession(summary) {
  const datasetName = summary.dataset === "kitti_tracking" ? "KITTI Tracking" : "MOT17";
  document.querySelector("#sequenceTitle").textContent = `${datasetName} · ${summary.sequence}`;
  document.querySelector("#verificationState").textContent = "Validated Stage 1–3 chain";
  document.querySelector(".session-state").classList.add("verified");
  seek.max = summary.timing.audio_duration_seconds;
  document.querySelector("#duration").textContent = formatTime(summary.timing.audio_duration_seconds);
  const rows = [
    ["Session ID", summary.session_id],
    ["Evidence", `${summary.counts.events.toLocaleString()} events · ${summary.counts.cues.toLocaleString()} cues`],
    ["Suppressions", summary.counts.suppressions.toLocaleString()],
    ["Media timing", `${summary.counts.frames} frames @ ${summary.timing.frame_rate} fps`],
    ["Audio", `${formatTime(summary.timing.audio_duration_seconds)} · ${summary.timing.sample_rate_hz.toLocaleString()} Hz`],
    ["WAV SHA-256", summary.audio.sha256],
  ];
  document.querySelector("#sessionDetails").innerHTML = rows.map(([name, value]) =>
    `<div><dt>${escapeHtml(name)}</dt><dd>${escapeHtml(value)}</dd></div>`).join("");
}

async function renderEvaluation(generation = state.generation) {
  const report = await getJson("/api/evaluation");
  if (generation !== state.generation) return;
  const tag = document.querySelector("#evaluationState");
  const grid = document.querySelector("#metricGrid");
  if (!report.available) {
    tag.textContent = "Unavailable";
    tag.classList.add("neutral");
    grid.innerHTML = '<div class="trace-empty">No verified Stage 3 report is declared for this session.</div>';
    return;
  }
  tag.textContent = "Verified";
  const metrics = report.metrics;
  const cards = [
    ["Eligible event coverage", formatPercent(metrics.event_coverage.eligible_event_coverage.value)],
    ["Source representation", formatPercent(metrics.event_coverage.source_representation_rate.value)],
    ["Cue density / second", formatNumber(metrics.cue_density.cues_per_second)],
    ["Peak concurrency", formatNumber(metrics.overlap_burden.peak_concurrency, 0)],
    ["Suppression rate", formatPercent(metrics.event_coverage.suppression_rate.value)],
    ["Fully traceable cues", formatPercent(metrics.traceability.fully_traceable_cue.value)],    
  ];
  grid.innerHTML = cards.map(([label, value]) =>
    `<div class="metric"><span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong></div>`).join("");
}

function outcomeFor(event) {
  const outcome = event.stage_2_outcome?.status;
  if (outcome === "represented" || outcome === "suppressed") return outcome;
  reportIntegrityAnomaly(event.event_id);
  return "anomaly";
}

function reportIntegrityAnomaly(eventId) {
  if (state.integrityAnomalies.has(eventId)) return;
  state.integrityAnomalies.add(eventId);
  const warning = document.querySelector("#integrityWarning");
  warning.textContent = "Evidence-integrity warning: an event has no retained cue or suppression outcome.";
  warning.hidden = false;
  console.error("evidence_integrity_anomaly:unresolved_stage_2_outcome");
}

function renderOverlay(frame) {
  overlay.setAttribute("viewBox", `0 0 ${frame.image.width} ${frame.image.height}`);
  overlay.replaceChildren();
  for (const event of frame.events) {
    const group = document.createElementNS("http://www.w3.org/2000/svg", "g");
    const outcome = outcomeFor(event);
    const rectangle = document.createElementNS("http://www.w3.org/2000/svg", "rect");
    rectangle.setAttribute("x", event.bbox.x);
    rectangle.setAttribute("y", event.bbox.y);
    rectangle.setAttribute("width", event.bbox.width);
    rectangle.setAttribute("height", event.bbox.height);
    rectangle.setAttribute("class", `event-box ${outcome}`);
    const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
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
      group.setAttribute("aria-label", `Select ${event.object_class} track ${event.track_id} cue at frame ${event.frame}`);
      const selectRepresentedCue = () => selectCue(cueId).catch((error) => notice(error.message));
      group.addEventListener("click", selectRepresentedCue);
      group.addEventListener("keydown", (keyboardEvent) => {
        if (keyboardEvent.key !== "Enter" && keyboardEvent.key !== " ") return;
        keyboardEvent.preventDefault();
        keyboardEvent.stopPropagation();
        selectRepresentedCue();
      });
    }
    group.append(rectangle, label);
    overlay.append(group);
  }
  updateCueSelection();
}

function setFrameContext(context) {
  if (context === state.frameContext) return;
  state.frameContext = context;
  document.querySelector("#frameKind").textContent =
    context === "cue" ? "Cue source frame" : "Playback frame";
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
    const image = document.querySelector("#sourceImage");
    image.onload = () => {
      if (generation === state.generation) document.querySelector("#viewerLoading").hidden = true;
    };
    image.src = imageUrl;
    preloadFollowingFrames(frame.frame, generation);
    document.querySelector("#frameNumber").textContent = String(frame.frame).padStart(3, "0");
    document.querySelector("#frameTime").textContent = `${frame.timestamp_seconds.toFixed(3)} s`;
    renderOverlay(frame);
    renderFrameCues();
  } finally {
    if (requestId === state.frameRequest) state.framePending = false;
  }
}

function prepareFrameImage(frameNumber, imageUrl) {
  const existing = state.preloadImages.get(frameNumber);
  if (existing) return existing.promise;
  const image = new Image();
  const entry = { image, promise: null };
  const imagePromise = new Promise((resolve, reject) => {
    image.onload = () => resolve(image);
    image.onerror = () => reject(new Error("frame_image_unavailable"));
  });
  entry.promise = imagePromise.finally(() => {
    if (state.preloadImages.get(frameNumber) === entry) {
      state.preloadImages.delete(frameNumber);
    }
  });
  state.preloadImages.set(frameNumber, entry);
  image.src = imageUrl;
  return entry.promise;
}

function preloadFollowingFrames(frameNumber, generation) {
  if (!state.session || generation !== state.generation) return;
  for (const nextFrame of [frameNumber + 1, frameNumber + 2]) {
    if (nextFrame >= state.session.counts.frames) break;
    if (state.preloadImages.size >= 2) break;
    prepareFrameImage(nextFrame, withSession(`/api/frames/${nextFrame}/image`))
      .catch(() => {});
  }
}

function resizeTimeline() {
  const ratio = window.devicePixelRatio || 1;
  const width = Math.max(300, timelineCanvas.clientWidth);
  timelineCanvas.width = Math.floor(width * ratio);
  timelineCanvas.height = Math.floor(198 * ratio);
  timelineBaseCanvas.width = Math.floor(width * ratio);
  timelineBaseCanvas.height = Math.floor(198 * ratio);
  timelineContext.setTransform(ratio, 0, 0, ratio, 0, 0);
  timelineBaseContext.setTransform(ratio, 0, 0, ratio, 0, 0);
  rebuildTimelineBase();
  drawTimeline();
}

function timelineX(timestamp, width) {
  const windowData = state.timeline.window;
  return ((timestamp - windowData.start_seconds) /
    (windowData.end_seconds - windowData.start_seconds)) * width;
}

function frameForTime(timestampSeconds, frameRate, frameCount) {
  const boundedTime = Math.max(0, timestampSeconds);
  return Math.min(Math.floor(boundedTime * frameRate), frameCount - 1);
}

function cueInspectionIsAligned() {
  return state.selectedCueFrame !== null &&
    state.selectedCueTime !== null &&
    audio.paused &&
    Math.abs(audio.currentTime - state.selectedCueTime) <= 1e-6;
}

function drawCurrentFrameInterval(height, width) {
  if (!state.session || !state.timeline) return;
  const frameRate = state.session.timing.frame_rate;
  const windowStart = state.timeline.window.start_seconds;
  const windowEnd = state.timeline.window.end_seconds;
  const playbackFrame = cueInspectionIsAligned()
    ? state.selectedCueFrame
    : frameForTime(audio.currentTime, frameRate, state.session.counts.frames);
  const frameStart = playbackFrame / frameRate;
  const frameEnd = (playbackFrame + 1) / frameRate;
  const highlightStart = Math.max(windowStart, frameStart);
  const highlightEnd = Math.min(windowEnd, frameEnd);
  if (highlightEnd > highlightStart) {
    timelineContext.fillStyle = "rgba(117, 240, 193, 0.09)";
    timelineContext.fillRect(
      timelineX(highlightStart, width),
      0,
      timelineX(highlightEnd, width) - timelineX(highlightStart, width),
      height,
    );
  }
}

function drawFrameBoundaries(context, height, width) {
  if (!state.session || !state.timeline) return;
  const frameRate = state.session.timing.frame_rate;
  const windowStart = state.timeline.window.start_seconds;
  const windowEnd = state.timeline.window.end_seconds;
  const firstBoundaryFrame = Math.ceil(windowStart * frameRate);
  const lastBoundaryFrame = Math.floor(windowEnd * frameRate);
  const pixelsPerFrame = width / ((windowEnd - windowStart) * frameRate);
  context.strokeStyle = "rgba(140, 163, 157, 0.18)";
  context.lineWidth = 1;
  context.fillStyle = "rgba(140, 163, 157, 0.72)";
  context.font = "9px ui-monospace, monospace";
  for (let frame = firstBoundaryFrame; frame <= lastBoundaryFrame; frame += 1) {
    const boundaryTime = frame / frameRate;
    if (boundaryTime < windowStart || boundaryTime > windowEnd) continue;
    const x = timelineX(boundaryTime, width);
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
  const height = 198;
  timelineBaseContext.clearRect(0, 0, width, height);
  timelineBaseContext.strokeStyle = "#172c28";
  timelineBaseContext.lineWidth = 1;
  for (let lane = 1; lane < 3; lane += 1) {
    timelineBaseContext.beginPath(); timelineBaseContext.moveTo(0, lane * 66); timelineBaseContext.lineTo(width, lane * 66); timelineBaseContext.stroke();
  }
  if (!state.timeline) return;
  drawFrameBoundaries(timelineBaseContext, height, width);
  drawMarkers(timelineBaseContext, state.timeline.events, 0, "#65b8ff", "timestamp_seconds", height, width);
  drawMarkers(timelineBaseContext, state.timeline.cues, 1, "#75f0c1", "start_time_seconds", height, width);
  drawMarkers(timelineBaseContext, state.timeline.suppressions, 2, "#ff718d", "timestamp_seconds", height, width);
}

function drawTimeline() {
  const width = timelineCanvas.clientWidth;
  const height = 198;
  timelineContext.clearRect(0, 0, width, height);
  timelineContext.fillStyle = "#07110f";
  timelineContext.fillRect(0, 0, width, height);
  if (!state.timeline) return;
  drawCurrentFrameInterval(height, width);
  timelineContext.drawImage(
    timelineBaseCanvas,
    0,
    0,
    timelineBaseCanvas.width,
    timelineBaseCanvas.height,
    0,
    0,
    width,
    height,
  );
  const selected = state.timeline.cues.find((cue) => cue.cue_id === state.selectedCue);
  if (selected) {
    const selectedX = timelineX(selected.start_time_seconds, width);
    timelineContext.strokeStyle = "#ffffff";
    timelineContext.lineWidth = 2;
    timelineContext.strokeRect(selectedX - 3.5, 76, 7, 46);
  }
  const cursor = timelineX(audio.currentTime, width);
  timelineContext.strokeStyle = "#ffffff";
  timelineContext.lineWidth = 1.5;
  timelineContext.beginPath(); timelineContext.moveTo(cursor, 0); timelineContext.lineTo(cursor, height); timelineContext.stroke();
  timelineContext.fillStyle = "#ffffff";
  timelineContext.beginPath(); timelineContext.moveTo(cursor - 4, 0); timelineContext.lineTo(cursor + 4, 0); timelineContext.lineTo(cursor, 6); timelineContext.fill();
}

function cueAtCanvasPoint(event) {
  if (!state.timeline) return null;
  const bounds = timelineCanvas.getBoundingClientRect();
  const x = event.clientX - bounds.left;
  const y = event.clientY - bounds.top;
  const laneHeight = bounds.height / 3;
  if (y < laneHeight + 8 || y > (2 * laneHeight) - 8) return null;
  let closest = null;
  let closestDistance = CUE_HIT_RADIUS_PX + 1;
  for (const cue of state.timeline.cues) {
    const cueX = timelineX(cue.start_time_seconds, bounds.width);
    const distance = Math.abs(cueX - x);
    if (distance <= CUE_HIT_RADIUS_PX && distance < closestDistance) {
      closest = cue;
      closestDistance = distance;
    }
  }
  return closest;
}

function compareCueOrder(a, b) {
  const timeDifference = a.start_time_seconds - b.start_time_seconds;
  if (timeDifference !== 0) return timeDifference;
  const trackDifference = String(a.track_id).localeCompare(
    String(b.track_id),
    undefined,
    { numeric: true },
  );
  if (trackDifference !== 0) return trackDifference;
  return a.cue_id.localeCompare(b.cue_id);
}

function renderFrameCues() {
  const container = document.querySelector("#frameCues");
  const cues = [...(state.frame?.cues || [])].sort(compareCueOrder);
  const frameNumber = state.frame?.frame;
  document.querySelector("#frameCueSummary").textContent = Number.isInteger(frameNumber)
    ? `Frame ${String(frameNumber).padStart(3, "0")} · ${cues.length} ${cues.length === 1 ? "cue" : "cues"}`
    : "—";
  container.replaceChildren();
  if (cues.length === 0) {
    const empty = document.createElement("p");
    empty.className = "cue-empty";
    empty.textContent = `No generated cues on frame ${String(frameNumber).padStart(3, "0")}.`;
    container.append(empty);
    return;
  }
  for (const cue of cues) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `cue-chip${state.selectedCue === cue.cue_id ? " active" : ""}`;
    button.setAttribute("aria-pressed", String(state.selectedCue === cue.cue_id));
    button.textContent = `${cue.start_time_seconds.toFixed(3)}s · ${cue.object_class} · t${cue.track_id}`;
    button.title = cue.cue_id;
    button.addEventListener("click", () => selectCue(cue.cue_id));
    container.append(button);
  }
}

function cachedTimelineCovers(time) {
  if (!state.timeline || !state.session) return false;
  const start = state.timeline.window.start_seconds;
  const end = state.timeline.window.end_seconds;
  const duration = state.session.timing.audio_duration_seconds;
  const lowerBound = start <= 0
    ? start
    : start + TIMELINE_EDGE_MARGIN_SECONDS;
  const upperBound = end >= duration
    ? end
    : end - TIMELINE_EDGE_MARGIN_SECONDS;
  return time >= lowerBound && time <= upperBound;
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
  const { start, end } = timelineWindowFor(time);
  const requestKey = `${start.toFixed(6)}:${end.toFixed(6)}`;
  if (!force && state.timelinePendingKey !== null) return;
  const requestId = ++state.timelineRequest;
  state.timelinePendingKey = requestKey;
  try {
    const timeline = await getJson(`/api/timeline?start=${start.toFixed(6)}&end=${end.toFixed(6)}`);
    if (generation !== state.generation || requestId !== state.timelineRequest) return;
    state.timeline = timeline;
    document.querySelector("#windowLabel").textContent = `${state.timeline.window.start_seconds.toFixed(3)}–${state.timeline.window.end_seconds.toFixed(3)} s`;
    rebuildTimelineBase();
  } finally {
    if (requestId === state.timelineRequest) state.timelinePendingKey = null;
  }
}

function updateCueSelection() {
  for (const button of document.querySelectorAll("#frameCues .cue-chip")) {
    const isActive = button.title === state.selectedCue;
    button.classList.toggle("active", isActive);
    button.setAttribute("aria-pressed", String(isActive));
  }
  for (const control of overlay.querySelectorAll(".event-cue-control")) {
    const isActive = control.getAttribute("data-cue-id") === state.selectedCue;
    control.classList.toggle("selected", isActive);
    control.setAttribute("aria-pressed", String(isActive));
  }
}

function traceNode(title, lines) {
  return `<section class="trace-node"><h3>${escapeHtml(title)}</h3>${lines.map(([label, value]) =>
    `<p>${escapeHtml(label)}<br><strong>${escapeHtml(value)}</strong></p>`).join("")}</section>`;
}

function renderTrace(trace) {
  document.querySelector("#traceState").textContent = "Complete chain";
  document.querySelector("#traceState").classList.remove("neutral");
  const shortCue = trace.cue.cue_id.replace("cue:", "").slice(0, 12);
  const shortEvent = trace.event.event_id.split(":").slice(-3).join(":");
  document.querySelector("#traceContent").className = "trace-chain";
  document.querySelector("#traceContent").innerHTML = [
    traceNode("Cue", [
      ["ID", shortCue],
      ["Start (event timestamp)", `${trace.cue.start_time_seconds.toFixed(6)} s`],
      ["Frequency (vertical centre)", `${trace.cue.frequency_hz.toFixed(1)} Hz`],
      ["Stereo pan (horizontal centre)", trace.cue.stereo_pan],
      ["Amplitude (box area)", trace.cue.amplitude],
      ["Duration", `${trace.cue.duration_seconds.toFixed(3)} s`],
    ]),
    traceNode("Event", [["ID", shortEvent], ["Source frame / track", `${trace.event.frame} / ${trace.event.track_id}`], ["Class", trace.event.object_class]]),
    traceNode("Annotation", [["Logical source", trace.source_annotation.logical_path], ["Physical row", trace.source_annotation.row]]),
    traceNode("Configuration", [["Preset", `${trace.configuration.preset.name} ${trace.configuration.preset.version}`], ["Renderer", `${trace.configuration.renderer.name} ${trace.configuration.renderer.version}`], ["Class modifier", "Recorded for traceability; not applied to waveform"]]),
    traceNode("Render", [["Samples", `${trace.render.start_sample}–${trace.render.end_sample_exclusive}`], ["Duration", `${trace.render.duration_samples} @ ${trace.render.sample_rate_hz} Hz`]]),
  ].join("");
  updateCueSelection();
  drawTimeline();
}

async function selectCue(cueId) {
  const generation = state.generation;
  const requestId = ++state.traceRequest;
  const cueIsInCurrentWindow = state.timeline?.cues.some((cue) => cue.cue_id === cueId) ?? false;
  const trace = await getJson(`/api/trace?cue_id=${encodeURIComponent(cueId)}`);
  if (generation !== state.generation || requestId !== state.traceRequest) return;
  audio.pause();
  audio.currentTime = trace.cue.start_time_seconds;
  state.lastPlaybackTime = audio.currentTime;
  state.selectedCue = cueId;
  state.selectedCueFrame = trace.event.frame;
  state.selectedCueTime = trace.cue.start_time_seconds;
  updateTransportPresentation(audio.currentTime);
  drawTimeline();
  await loadFrame(trace.event.frame, "cue");
  if (generation !== state.generation || requestId !== state.traceRequest) return;
  if (!cueIsInCurrentWindow) {
    await loadTimeline(true);
    if (generation !== state.generation || requestId !== state.traceRequest) return;
  }
  renderTrace(trace);
}

function clearCueFrameAlignment() {
  state.selectedCueFrame = null;
  state.selectedCueTime = null;
  setFrameContext("playback");
}

function setAudioTime(value) {
  const duration = state.session?.timing.audio_duration_seconds || audio.duration || 0;
  clearCueFrameAlignment();
  audio.currentTime = Math.min(Math.max(value, 0), duration);
  updateTransportPresentation(audio.currentTime);
  loadTimeline().catch((error) => notice(error.message));
}

function resetSessionState(sessionId) {
  state.generation += 1;
  state.sessionId = sessionId;
  state.session = null;
  state.frame = null;
  state.frameNumber = -1;
  state.frameContext = null;
  state.framePending = false;
  state.timeline = null;
  state.timelinePendingKey = null;
  state.selectedCue = null;
  state.selectedCueFrame = null;
  state.selectedCueTime = null;
  state.traceRequest += 1;
  state.frameRequest += 1;
  state.timelineRequest += 1;
  state.integrityAnomalies.clear();
  state.lastPlaybackTime = null;
  state.preloadImages.clear();

  audio.pause();
  audio.removeAttribute("src");
  audio.load();
  seek.max = 1;
  updateTransportPresentation(0);
  playPause.textContent = "▶";
  playPause.setAttribute("aria-label", "Play");
  document.querySelector("#duration").textContent = "00:00.000";
  document.querySelector("#sequenceTitle").textContent = "Loading…";
  document.querySelector("#frameKind").textContent = "Playback frame";
  document.querySelector("#frameNumber").textContent = "—";
  document.querySelector("#frameTime").textContent = "—";
  document.querySelector("#windowLabel").textContent = "—";
  const integrityWarning = document.querySelector("#integrityWarning");
  integrityWarning.textContent = "";
  integrityWarning.hidden = true;
  document.querySelector("#verificationState").textContent = "Opening verified session…";
  document.querySelector(".session-state").classList.remove("verified");
  const image = document.querySelector("#sourceImage");
  image.onload = null;
  image.removeAttribute("src");
  document.querySelector("#viewerLoading").hidden = false;
  overlay.replaceChildren();
  document.querySelector("#frameCueSummary").textContent = "—";
  document.querySelector("#frameCues").replaceChildren();
  document.querySelector("#sessionDetails").replaceChildren();
  const evaluationState = document.querySelector("#evaluationState");
  evaluationState.textContent = "Checking";
  evaluationState.className = "evidence-tag";
  document.querySelector("#metricGrid").innerHTML =
    '<div class="skeleton"></div><div class="skeleton"></div><div class="skeleton"></div><div class="skeleton"></div>';
  const traceState = document.querySelector("#traceState");
  traceState.textContent = "Select a cue";
  traceState.className = "evidence-tag neutral";
  const traceContent = document.querySelector("#traceContent");
  traceContent.className = "trace-empty";
  traceContent.textContent = "Choose a cue marker or frame cue to inspect its verified source and rendered sample chain.";
  const noticeElement = document.querySelector("#notice");
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
  await Promise.all([renderEvaluation(generation), loadFrame(0), loadTimeline(true)]);
  if (generation === state.generation) resizeTimeline();
}

function tick() {
  if (state.session) {
    const time = audio.currentTime;
    if (time !== state.lastPlaybackTime) {
      state.lastPlaybackTime = time;
      updateTransportPresentation(time);
      const inspectingCue = cueInspectionIsAligned();
      const frame = inspectingCue
        ? state.selectedCueFrame
        : frameForTime(time, state.session.timing.frame_rate, state.session.counts.frames);
      if (frame !== state.frameNumber && !state.framePending) {
        loadFrame(frame, inspectingCue ? "cue" : "playback").catch((error) => notice(error.message));
      }
      loadTimeline().catch((error) => notice(error.message));
      drawTimeline();
    }
  }
  window.requestAnimationFrame(tick);
}

playPause.addEventListener("click", async () => {
  if (!state.session) return;
  if (audio.paused) await audio.play(); else audio.pause();
});
audio.addEventListener("play", () => {
  clearCueFrameAlignment();
  playPause.textContent = "❚❚";
  playPause.setAttribute("aria-label", "Pause");
});
audio.addEventListener("pause", () => { playPause.textContent = "▶"; playPause.setAttribute("aria-label", "Play"); });
seek.addEventListener("input", () => setAudioTime(Number(seek.value)));
document.querySelector("#stepBack").addEventListener("click", () => { if (state.session) { audio.pause(); setAudioTime(audio.currentTime - 1 / state.session.timing.frame_rate); } });
document.querySelector("#stepForward").addEventListener("click", () => { if (state.session) { audio.pause(); setAudioTime(audio.currentTime + 1 / state.session.timing.frame_rate); } });
document.querySelector("#mute").addEventListener("click", (event) => { audio.muted = !audio.muted; event.currentTarget.textContent = audio.muted ? "Muted" : "Audio on"; });
timelineCanvas.addEventListener("click", (event) => {
  const cue = cueAtCanvasPoint(event);
  if (cue) selectCue(cue.cue_id).catch((error) => notice(error.message));
});
timelineCanvas.addEventListener("mousemove", (event) => {
  timelineCanvas.style.cursor = cueAtCanvasPoint(event) ? "pointer" : "default";
});
timelineCanvas.addEventListener("mouseleave", () => { timelineCanvas.style.cursor = "default"; });
window.addEventListener("resize", resizeTimeline);
window.addEventListener("keydown", (event) => {
  if (event.target instanceof HTMLInputElement || event.target instanceof HTMLSelectElement) return;
  if (event.code === "Space") { event.preventDefault(); playPause.click(); }
  if (event.code === "ArrowLeft") { event.preventDefault(); document.querySelector("#stepBack").click(); }
  if (event.code === "ArrowRight") { event.preventDefault(); document.querySelector("#stepForward").click(); }
});

async function initialise() {
  try {
    state.catalogue = await getJson("/api/sessions", null);
    sessionSelect.replaceChildren();
    for (const session of state.catalogue.sessions) {
      const option = document.createElement("option");
      option.value = session.session_id;
      const datasetName = session.dataset === "kitti_tracking" ? "KITTI Tracking" : "MOT17";
      option.textContent = `${datasetName} · ${session.sequence}`;
      sessionSelect.append(option);
    }
    sessionSelect.disabled = false;
    sessionSelect.addEventListener("change", () => {
      switchSession(sessionSelect.value).catch((error) => {
        document.querySelector("#verificationState").textContent = "Session unavailable";
        notice(error.message);
      });
    });
    await switchSession(state.catalogue.default_session_id);
    window.requestAnimationFrame(tick);
  } catch (error) {
    document.querySelector("#verificationState").textContent = "Session unavailable";
    notice(error.message);
  }
}

initialise();
