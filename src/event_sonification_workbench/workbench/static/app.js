"use strict";

const audio = document.querySelector("#audio");
const seek = document.querySelector("#seek");
const playPause = document.querySelector("#playPause");
const sessionSelect = document.querySelector("#sessionSelect");
const timelineCanvas = document.querySelector("#timeline");
const timelineContext = timelineCanvas.getContext("2d");
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
  timeline: null,
  timelinePendingKey: null,
  timelineRequest: 0,
  selectedCue: null,
  selectedCueFrame: null,
  selectedCueTime: null,
  traceRequest: 0,
  frameRequest: 0,
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
    ["P95 alignment (samples)", formatNumber(metrics.timing_alignment.end_to_end.samples.p95, 0)],
    ["Byte reproducibility", metrics.reproducibility.byte.equal ? "Identical" : "Mismatch"],
  ];
  grid.innerHTML = cards.map(([label, value]) =>
    `<div class="metric"><span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong></div>`).join("");
}

function outcomeFor(event) {
  return event.stage_2_outcome?.status || "unresolved";
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
    group.append(rectangle, label);
    overlay.append(group);
  }
}

function setFrameContext(context) {
  document.querySelector("#frameKind").textContent =
    context === "cue" ? "Cue source frame" : "Playback frame";
}

async function loadFrame(frameNumber, context = "playback") {
  setFrameContext(context);
  if (frameNumber === state.frameNumber) return;
  state.frameNumber = frameNumber;
  const generation = state.generation;
  const requestId = ++state.frameRequest;
  const frame = await getJson(`/api/frames/${frameNumber}`);
  if (generation !== state.generation || requestId !== state.frameRequest) return;
  state.frame = frame;
  const image = document.querySelector("#sourceImage");
  image.onload = () => {
    if (generation === state.generation) document.querySelector("#viewerLoading").hidden = true;
  };
  image.src = withSession(frame.image_url);
  document.querySelector("#frameNumber").textContent = String(frame.frame).padStart(3, "0");
  document.querySelector("#frameTime").textContent = `${frame.timestamp_seconds.toFixed(3)} s`;
  renderOverlay(frame);
}

function resizeTimeline() {
  const ratio = window.devicePixelRatio || 1;
  const width = Math.max(300, timelineCanvas.clientWidth);
  timelineCanvas.width = Math.floor(width * ratio);
  timelineCanvas.height = Math.floor(198 * ratio);
  timelineContext.setTransform(ratio, 0, 0, ratio, 0, 0);
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

function drawFrameStructure(height, width) {
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

  const firstBoundaryFrame = Math.ceil(windowStart * frameRate);
  const lastBoundaryFrame = Math.floor(windowEnd * frameRate);
  const pixelsPerFrame = width / ((windowEnd - windowStart) * frameRate);
  timelineContext.strokeStyle = "rgba(140, 163, 157, 0.18)";
  timelineContext.lineWidth = 1;
  timelineContext.fillStyle = "rgba(140, 163, 157, 0.72)";
  timelineContext.font = "9px ui-monospace, monospace";
  for (let frame = firstBoundaryFrame; frame <= lastBoundaryFrame; frame += 1) {
    const boundaryTime = frame / frameRate;
    if (boundaryTime < windowStart || boundaryTime > windowEnd) continue;
    const x = timelineX(boundaryTime, width);
    timelineContext.beginPath();
    timelineContext.moveTo(x, 0);
    timelineContext.lineTo(x, height);
    timelineContext.stroke();
    if (pixelsPerFrame >= 32 && x <= width - 18) {
      timelineContext.fillText(`f${frame}`, x + 3, 10);
    }
  }
}

function drawMarkers(items, lane, color, timestampField, height, width) {
  const laneHeight = height / 3;
  const y = lane * laneHeight;
  timelineContext.fillStyle = color;
  for (const item of items) {
    const x = timelineX(item[timestampField], width);
    timelineContext.fillRect(Math.max(0, x - 0.65), y + 12, 1.3, laneHeight - 24);
  }
}

function drawTimeline() {
  const width = timelineCanvas.clientWidth;
  const height = 198;
  timelineContext.clearRect(0, 0, width, height);
  timelineContext.fillStyle = "#07110f";
  timelineContext.fillRect(0, 0, width, height);
  timelineContext.strokeStyle = "#172c28";
  timelineContext.lineWidth = 1;
  for (let lane = 1; lane < 3; lane += 1) {
    timelineContext.beginPath(); timelineContext.moveTo(0, lane * 66); timelineContext.lineTo(width, lane * 66); timelineContext.stroke();
  }
  if (!state.timeline) return;
  drawFrameStructure(height, width);
  drawMarkers(state.timeline.events, 0, "#65b8ff", "timestamp_seconds", height, width);
  drawMarkers(state.timeline.cues, 1, "#75f0c1", "start_time_seconds", height, width);
  drawMarkers(state.timeline.suppressions, 2, "#ff718d", "timestamp_seconds", height, width);
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

function renderNearbyCues() {
  const container = document.querySelector("#nearbyCues");
  const cues = [...state.timeline.cues]
    .sort((a, b) => Math.abs(a.start_time_seconds - audio.currentTime) - Math.abs(b.start_time_seconds - audio.currentTime))
    .slice(0, 10);
  container.replaceChildren();
  for (const cue of cues) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `cue-chip${state.selectedCue === cue.cue_id ? " active" : ""}`;
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
  if (!force && state.timelinePendingKey === requestKey) return;
  const requestId = ++state.timelineRequest;
  state.timelinePendingKey = requestKey;
  try {
    const timeline = await getJson(`/api/timeline?start=${start.toFixed(6)}&end=${end.toFixed(6)}`);
    if (generation !== state.generation || requestId !== state.timelineRequest) return;
    state.timeline = timeline;
    document.querySelector("#windowLabel").textContent = `${state.timeline.window.start_seconds.toFixed(3)}–${state.timeline.window.end_seconds.toFixed(3)} s`;
    renderNearbyCues();
    if (state.frame) renderOverlay(state.frame);
  } finally {
    if (requestId === state.timelineRequest) state.timelinePendingKey = null;
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
      ["Class modifier (trace only)", trace.cue.class_modifier],
    ]),
    traceNode("Event", [["ID", shortEvent], ["Source frame / track", `${trace.event.frame} / ${trace.event.track_id}`], ["Class", trace.event.object_class]]),
    traceNode("Annotation", [["Logical source", trace.source_annotation.logical_path], ["Physical row", trace.source_annotation.row]]),
    traceNode("Configuration", [["Preset", `${trace.configuration.preset.name} ${trace.configuration.preset.version}`], ["Renderer", `${trace.configuration.renderer.name} ${trace.configuration.renderer.version}`], ["Class modifier", "Recorded for traceability; not applied to waveform"]]),
    traceNode("Render", [["Samples", `${trace.render.start_sample}–${trace.render.end_sample_exclusive}`], ["Duration", `${trace.render.duration_samples} @ ${trace.render.sample_rate_hz} Hz`]]),
  ].join("");
  renderNearbyCues();
  drawTimeline();
}

async function selectCue(cueId) {
  const generation = state.generation;
  const requestId = ++state.traceRequest;
  const trace = await getJson(`/api/trace?cue_id=${encodeURIComponent(cueId)}`);
  if (generation !== state.generation || requestId !== state.traceRequest) return;
  audio.pause();
  audio.currentTime = trace.cue.start_time_seconds;
  seek.value = trace.cue.start_time_seconds;
  state.selectedCue = cueId;
  state.selectedCueFrame = trace.event.frame;
  state.selectedCueTime = trace.cue.start_time_seconds;
  await loadFrame(trace.event.frame, "cue");
  if (generation !== state.generation || requestId !== state.traceRequest) return;
  await loadTimeline(true);
  if (generation !== state.generation || requestId !== state.traceRequest) return;
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
  loadTimeline(true).catch((error) => notice(error.message));
}

function resetSessionState(sessionId) {
  state.generation += 1;
  state.sessionId = sessionId;
  state.session = null;
  state.frame = null;
  state.frameNumber = -1;
  state.timeline = null;
  state.timelinePendingKey = null;
  state.selectedCue = null;
  state.selectedCueFrame = null;
  state.selectedCueTime = null;
  state.traceRequest += 1;
  state.frameRequest += 1;
  state.timelineRequest += 1;

  audio.pause();
  audio.removeAttribute("src");
  audio.load();
  seek.value = 0;
  seek.max = 1;
  playPause.textContent = "▶";
  playPause.setAttribute("aria-label", "Play");
  document.querySelector("#currentTime").textContent = "00:00.000";
  document.querySelector("#duration").textContent = "00:00.000";
  document.querySelector("#sequenceTitle").textContent = "Loading…";
  document.querySelector("#frameKind").textContent = "Playback frame";
  document.querySelector("#frameNumber").textContent = "—";
  document.querySelector("#frameTime").textContent = "—";
  document.querySelector("#windowLabel").textContent = "—";
  document.querySelector("#verificationState").textContent = "Opening verified session…";
  document.querySelector(".session-state").classList.remove("verified");
  const image = document.querySelector("#sourceImage");
  image.onload = null;
  image.removeAttribute("src");
  document.querySelector("#viewerLoading").hidden = false;
  overlay.replaceChildren();
  document.querySelector("#nearbyCues").replaceChildren();
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
  traceContent.textContent = "Choose a cue marker or nearby cue to inspect its verified source and rendered sample chain.";
  const noticeElement = document.querySelector("#notice");
  noticeElement.textContent = "";
  noticeElement.classList.remove("show");
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
    seek.value = time;
    document.querySelector("#currentTime").textContent = formatTime(time);
    const inspectingCue = cueInspectionIsAligned();
    const frame = inspectingCue
      ? state.selectedCueFrame
      : frameForTime(time, state.session.timing.frame_rate, state.session.counts.frames);
    loadFrame(frame, inspectingCue ? "cue" : "playback").catch((error) => notice(error.message));
    loadTimeline().catch((error) => notice(error.message));
    drawTimeline();
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
