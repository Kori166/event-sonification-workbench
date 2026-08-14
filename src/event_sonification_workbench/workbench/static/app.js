"use strict";

const audio = document.querySelector("#audio");
const seek = document.querySelector("#seek");
const playPause = document.querySelector("#playPause");
const timelineCanvas = document.querySelector("#timeline");
const timelineContext = timelineCanvas.getContext("2d");
const overlay = document.querySelector("#eventOverlay");
const state = {
  session: null,
  frame: null,
  frameNumber: -1,
  timeline: null,
  timelineLoading: false,
  selectedCue: null,
  frameRequest: 0,
};

function notice(message) {
  const element = document.querySelector("#notice");
  element.textContent = message;
  element.classList.add("show");
  window.setTimeout(() => element.classList.remove("show"), 4000);
}

async function getJson(url) {
  const response = await fetch(url, { headers: { Accept: "application/json" } });
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
  document.querySelector("#sequenceTitle").textContent = `${summary.dataset.toUpperCase()} · ${summary.sequence}`;
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

async function renderEvaluation() {
  const report = await getJson("/api/evaluation");
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

function outcomeFor(eventId) {
  if (!state.timeline) return "event-only";
  if (state.timeline.cues.some((cue) => cue.source_event_id === eventId)) return "represented";
  if (state.timeline.suppressions.some((item) => item.source_event_id === eventId)) return "suppressed";
  return "event-only";
}

function renderOverlay(frame) {
  overlay.setAttribute("viewBox", `0 0 ${frame.image.width} ${frame.image.height}`);
  overlay.replaceChildren();
  for (const event of frame.events) {
    const group = document.createElementNS("http://www.w3.org/2000/svg", "g");
    const outcome = outcomeFor(event.event_id);
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

async function loadFrame(frameNumber) {
  if (frameNumber === state.frameNumber) return;
  state.frameNumber = frameNumber;
  const requestId = ++state.frameRequest;
  const frame = await getJson(`/api/frames/${frameNumber}`);
  if (requestId !== state.frameRequest) return;
  state.frame = frame;
  const image = document.querySelector("#sourceImage");
  image.onload = () => { document.querySelector("#viewerLoading").hidden = true; };
  image.src = frame.image_url;
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
  drawMarkers(state.timeline.events, 0, "#65b8ff", "timestamp_seconds", height, width);
  drawMarkers(state.timeline.cues, 1, "#75f0c1", "start_time_seconds", height, width);
  drawMarkers(state.timeline.suppressions, 2, "#ff718d", "timestamp_seconds", height, width);
  const cursor = timelineX(audio.currentTime, width);
  timelineContext.strokeStyle = "#ffffff";
  timelineContext.lineWidth = 1.5;
  timelineContext.beginPath(); timelineContext.moveTo(cursor, 0); timelineContext.lineTo(cursor, height); timelineContext.stroke();
  timelineContext.fillStyle = "#ffffff";
  timelineContext.beginPath(); timelineContext.moveTo(cursor - 4, 0); timelineContext.lineTo(cursor + 4, 0); timelineContext.lineTo(cursor, 6); timelineContext.fill();
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
    button.addEventListener("click", () => loadTrace(cue.cue_id));
    container.append(button);
  }
}

async function loadTimeline(force = false) {
  if (!state.session || state.timelineLoading) return;
  const time = audio.currentTime;
  if (!force && state.timeline &&
      time > state.timeline.window.start_seconds + 0.25 &&
      time < state.timeline.window.end_seconds - 0.25) return;
  state.timelineLoading = true;
  const duration = state.session.timing.audio_duration_seconds;
  let start = Math.max(0, time - 0.35);
  let end = Math.min(duration, start + 1);
  start = Math.max(0, end - 1);
  try {
    state.timeline = await getJson(`/api/timeline?start=${start.toFixed(6)}&end=${end.toFixed(6)}`);
    document.querySelector("#windowLabel").textContent = `${state.timeline.window.start_seconds.toFixed(3)}–${state.timeline.window.end_seconds.toFixed(3)} s`;
    renderNearbyCues();
    if (state.frame) renderOverlay(state.frame);
  } finally {
    state.timelineLoading = false;
  }
}

function traceNode(title, lines) {
  return `<section class="trace-node"><h3>${escapeHtml(title)}</h3>${lines.map(([label, value]) =>
    `<p>${escapeHtml(label)}<br><strong>${escapeHtml(value)}</strong></p>`).join("")}</section>`;
}

async function loadTrace(cueId) {
  const trace = await getJson(`/api/trace?cue_id=${encodeURIComponent(cueId)}`);
  state.selectedCue = cueId;
  document.querySelector("#traceState").textContent = "Complete chain";
  document.querySelector("#traceState").classList.remove("neutral");
  const shortCue = trace.cue.cue_id.replace("cue:", "").slice(0, 12);
  const shortEvent = trace.event.event_id.split(":").slice(-3).join(":");
  document.querySelector("#traceContent").className = "trace-chain";
  document.querySelector("#traceContent").innerHTML = [
    traceNode("Cue", [["ID", shortCue], ["Start", `${trace.cue.start_time_seconds.toFixed(6)} s`], ["Signal", `${trace.cue.frequency_hz.toFixed(1)} Hz · pan ${trace.cue.stereo_pan}`]]),
    traceNode("Event", [["ID", shortEvent], ["Frame / track", `${trace.event.frame} / ${trace.event.track_id}`], ["Class", trace.event.object_class]]),
    traceNode("Annotation", [["Logical source", trace.source_annotation.logical_path], ["Physical row", trace.source_annotation.row]]),
    traceNode("Configuration", [["Preset", `${trace.configuration.preset.name} ${trace.configuration.preset.version}`], ["Renderer", `${trace.configuration.renderer.name} ${trace.configuration.renderer.version}`]]),
    traceNode("Render", [["Samples", `${trace.render.start_sample}–${trace.render.end_sample_exclusive}`], ["Duration", `${trace.render.duration_samples} @ ${trace.render.sample_rate_hz} Hz`]]),
  ].join("");
  renderNearbyCues();
}

function setAudioTime(value) {
  const duration = state.session?.timing.audio_duration_seconds || audio.duration || 0;
  audio.currentTime = Math.min(Math.max(value, 0), duration);
  loadTimeline(true).catch((error) => notice(error.message));
}

function tick() {
  if (state.session) {
    const time = audio.currentTime;
    seek.value = time;
    document.querySelector("#currentTime").textContent = formatTime(time);
    const frame = Math.min(Math.floor(time * state.session.timing.frame_rate + 1e-9), state.session.counts.frames - 1);
    loadFrame(frame).catch((error) => notice(error.message));
    loadTimeline().catch((error) => notice(error.message));
    drawTimeline();
  }
  window.requestAnimationFrame(tick);
}

playPause.addEventListener("click", async () => {
  if (audio.paused) await audio.play(); else audio.pause();
});
audio.addEventListener("play", () => { playPause.textContent = "❚❚"; playPause.setAttribute("aria-label", "Pause"); });
audio.addEventListener("pause", () => { playPause.textContent = "▶"; playPause.setAttribute("aria-label", "Play"); });
seek.addEventListener("input", () => setAudioTime(Number(seek.value)));
document.querySelector("#stepBack").addEventListener("click", () => { audio.pause(); setAudioTime(audio.currentTime - 1 / state.session.timing.frame_rate); });
document.querySelector("#stepForward").addEventListener("click", () => { audio.pause(); setAudioTime(audio.currentTime + 1 / state.session.timing.frame_rate); });
document.querySelector("#mute").addEventListener("click", (event) => { audio.muted = !audio.muted; event.currentTarget.textContent = audio.muted ? "Muted" : "Audio on"; });
timelineCanvas.addEventListener("click", (event) => {
  if (!state.timeline) return;
  const bounds = timelineCanvas.getBoundingClientRect();
  const clickedTime = state.timeline.window.start_seconds + ((event.clientX - bounds.left) / bounds.width) * (state.timeline.window.end_seconds - state.timeline.window.start_seconds);
  const nearest = state.timeline.cues.reduce((best, cue) => Math.abs(cue.start_time_seconds - clickedTime) < Math.abs(best.start_time_seconds - clickedTime) ? cue : best, state.timeline.cues[0]);
  if (nearest) loadTrace(nearest.cue_id).catch((error) => notice(error.message));
});
window.addEventListener("resize", resizeTimeline);
window.addEventListener("keydown", (event) => {
  if (event.target instanceof HTMLInputElement) return;
  if (event.code === "Space") { event.preventDefault(); playPause.click(); }
  if (event.code === "ArrowLeft") { event.preventDefault(); document.querySelector("#stepBack").click(); }
  if (event.code === "ArrowRight") { event.preventDefault(); document.querySelector("#stepForward").click(); }
});

async function initialise() {
  try {
    state.session = await getJson("/api/session");
    renderSession(state.session);
    await Promise.all([renderEvaluation(), loadFrame(0), loadTimeline(true)]);
    resizeTimeline();
    window.requestAnimationFrame(tick);
  } catch (error) {
    document.querySelector("#verificationState").textContent = "Session unavailable";
    notice(error.message);
  }
}

initialise();
