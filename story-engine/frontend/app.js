// ── STATE ──
const API = "";  // same origin
let sessionId = null;
let currentBeatIndex = 0;
let totalBeats = 0;
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;
let activeRecordTarget = null;

// ── INIT ──
window.addEventListener("DOMContentLoaded", async () => {
  const res = await fetch(`${API}/session/new`, { method: "POST" });
  const data = await res.json();
  sessionId = data.session_id;
});

// ── MODE SELECTION ──
function setMode(mode) {
  document.getElementById("btn-seed-mode").classList.toggle("active", mode === "seed");
  document.getElementById("btn-char-mode").classList.toggle("active", mode === "character");
  document.getElementById("seed-input").classList.toggle("hidden", mode !== "seed");
  document.getElementById("character-input").classList.toggle("hidden", mode !== "character");
}

// ── STORY INIT ──
async function initStory() {
  const isSeed = !document.getElementById("seed-input").classList.contains("hidden");
  let body;

  if (isSeed) {
    const seed = document.getElementById("seed-text").value.trim();
    if (!seed) { alert("Please enter a seed idea."); return; }
    body = { mode: "seed", seed };
  } else {
    const fields = ["char-name","char-background","char-core-gap","char-values","char-want","char-need",
                    "world-ethos","world-norms","world-enforcement","world-gap"];
    for (const f of fields) {
      if (!document.getElementById(f).value.trim()) {
        alert(`Please fill in: ${f.replace(/-/g," ")}`); return;
      }
    }
    body = {
      mode: "character",
      character: {
        name: v("char-name"), background: v("char-background"),
        core_gap: v("char-core-gap"), values: v("char-values"),
        surface_want: v("char-want"), deeper_need: v("char-need"),
      },
      world: {
        ethos: v("world-ethos"), norms: v("world-norms"),
        enforcement: v("world-enforcement"), world_gap: v("world-gap"),
      }
    };
  }

  showLoading("Building your story constitution...");

  try {
    const res = await fetch(`${API}/story/${sessionId}/init`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    renderConstitution(data);
    showScreen("screen-constitution");
  } catch (e) {
    alert("Error: " + e.message);
  } finally {
    hideLoading();
  }
}

function v(id) { return document.getElementById(id).value.trim(); }

// ── RENDER CONSTITUTION ──
function renderConstitution(data) {
  const c = data.constitution;
  document.getElementById("const-identity").textContent = c.core_identity;
  document.getElementById("const-engine").textContent = c.central_want_pain;
  document.getElementById("const-theme").textContent = c.theme;
  document.getElementById("const-emotion").textContent = c.emotional_signature;
  document.getElementById("const-protagonist").textContent =
    `${c.protagonist.name} — ${c.protagonist.core_gap}`;
  document.getElementById("const-world").textContent =
    `${c.world_contract.ethos}`;
  document.getElementById("const-voice").textContent =
    `${data.voice_style} — ${voiceDescription(data.voice_style)}`;

  const grid = document.getElementById("arc-candidates");
  grid.innerHTML = "";
  data.possibilities.candidates.forEach((arc, i) => {
    grid.innerHTML += `
      <div class="arc-card" id="arc-card-${i}" onclick="selectArc(${i})">
        <div class="arc-num">Arc ${i+1}</div>
        <h3>${arc.title}</h3>
        <div class="logline">${arc.logline}</div>
        <div class="arc-detail">
          <strong>Conflict:</strong> ${arc.core_conflict}<br>
          <strong>Transformation:</strong> ${arc.transformation}
        </div>
        <div class="arc-appeal">${arc.dramatic_appeal}</div>
        <button class="btn-choose">Choose this arc ✦</button>
      </div>`;
  });
}

function voiceDescription(style) {
  const map = {
    EPIC: "deep & dramatic", WHIMSICAL: "warm & playful",
    TENSE: "taut & urgent", LYRICAL: "melodic & poetic", NEUTRAL: "clear & present"
  };
  return map[style] || style;
}

// ── ARC SELECTION ──
async function selectArc(index) {
  document.querySelectorAll(".arc-card").forEach(c => c.classList.remove("selected"));
  document.getElementById(`arc-card-${index}`).classList.add("selected");

  showLoading("Crafting your story arc...");

  try {
    const res = await fetch(`${API}/story/${sessionId}/choose-arc`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ arc_index: index }),
    });
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();

    totalBeats = data.skeleton.beats.length;
    currentBeatIndex = 0;

    // init story screen
    document.getElementById("arc-title-display").textContent =
      data.skeleton.chosen_arc.title;

    renderBeatProgress(0);
    renderBeatsList(data.skeleton.beats);

    showScreen("screen-story");
    await loadNextScene();
  } catch (e) {
    alert("Error: " + e.message);
  } finally {
    hideLoading();
  }
}

// ── SCENE LOADING ──
async function loadNextScene(intervention = null) {
  showLoading("Writing the scene...");

  try {
    let url = `${API}/story/${sessionId}/next-scene`;
    if (intervention) url += `?intervention=${encodeURIComponent(intervention)}`;

    const res = await fetch(url, { method: "POST" });
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();

    if (data.done) {
      showComplete();
      return;
    }

    renderScene(data);
    currentBeatIndex = data.beat_index + 1;
    renderBeatProgress(data.beat_index);
    updateSidebar(data.scene.beat);

  } catch (e) {
    alert("Error generating scene: " + e.message);
  } finally {
    hideLoading();
  }
}

function renderScene(data) {
  const scene = data.scene;

  // image
  const imgContainer = document.getElementById("scene-image-container");
  const img = document.getElementById("scene-image");
  if (scene.image_url) {
    img.src = scene.image_url;
    imgContainer.classList.remove("hidden");
  } else {
    imgContainer.classList.add("hidden");
  }

  // beat label
  document.getElementById("scene-beat-label").textContent =
    scene.beat.arc_position.replace(/_/g, " ").toUpperCase();

  // prose with typewriter effect
  typewriterEffect("scene-prose", scene.prose);

  // enable/disable next
  document.getElementById("btn-next").disabled = false;
  document.getElementById("btn-next").textContent =
    data.is_final ? "Complete story ✦" : "Continue →";

  // mark beat done in sidebar
  document.querySelectorAll(".beat-item").forEach((el, i) => {
    if (i < currentBeatIndex) el.classList.add("done");
  });
}

function typewriterEffect(elementId, text) {
  const el = document.getElementById(elementId);
  el.textContent = "";
  let i = 0;
  const speed = 18;
  function tick() {
    if (i < text.length) {
      el.textContent += text[i++];
      setTimeout(tick, speed);
    }
  }
  tick();
}

// ── NEXT SCENE ──
async function nextScene() {
  document.getElementById("btn-next").disabled = true;
  document.getElementById("intervention-panel").classList.add("hidden");
  await loadNextScene();
}

// ── INTERVENTION ──
function toggleIntervention() {
  document.getElementById("intervention-panel").classList.toggle("hidden");
}

async function intervene() {
  const text = document.getElementById("intervention-text").value.trim();
  if (!text) { alert("Please describe how you want to redirect the story."); return; }
  document.getElementById("intervention-text").value = "";
  document.getElementById("intervention-panel").classList.add("hidden");
  await loadNextScene(text);
}

// ── NARRATION ──
async function narrateScene() {
  const beatIndex = currentBeatIndex - 1;
  if (beatIndex < 0) return;

  const btn = document.getElementById("btn-narrate");
  btn.textContent = "⏳ Generating...";
  btn.disabled = true;

  try {
    const res = await fetch(`${API}/story/${sessionId}/narrate/${beatIndex}`, {
      method: "POST"
    });
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();

    const audio = document.getElementById("narration-audio");
    audio.src = `data:${data.mime_type};base64,${data.audio_base64}`;
    audio.play();

    btn.textContent = "🔊 Narrating...";
    audio.onended = () => {
      btn.textContent = "🔊 Narrate";
      btn.disabled = false;
    };
  } catch (e) {
    alert("Narration error: " + e.message);
    btn.textContent = "🔊 Narrate";
    btn.disabled = false;
  }
}

// ── VOICE INPUT ──
async function toggleVoiceInput(targetId, btnId) {
  const btn = document.getElementById(btnId);

  if (isRecording && activeRecordTarget === targetId) {
    // stop recording
    mediaRecorder.stop();
    isRecording = false;
    btn.classList.remove("recording");
    btn.title = "Speak your idea";
    return;
  }

  if (!navigator.mediaDevices) {
    alert("Voice input not supported in this browser."); return;
  }

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    audioChunks = [];
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
    mediaRecorder.onstop = async () => {
      const blob = new Blob(audioChunks, { type: "audio/webm" });
      const reader = new FileReader();
      reader.onloadend = async () => {
        const base64 = reader.result.split(",")[1];
        btn.textContent = "⏳";
        try {
          const res = await fetch(`${API}/voice/transcribe`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ audio_base64: base64, mime_type: "audio/webm" }),
          });
          const data = await res.json();
          document.getElementById(targetId).value = data.text;
        } catch (e) {
          console.error("Transcription failed", e);
        }
        btn.textContent = "🎙";
        btn.title = "Speak your idea";
      };
      reader.readAsDataURL(blob);
      stream.getTracks().forEach(t => t.stop());
    };

    mediaRecorder.start();
    isRecording = true;
    activeRecordTarget = targetId;
    btn.classList.add("recording");
    btn.title = "Click to stop";
  } catch (e) {
    alert("Could not access microphone: " + e.message);
  }
}

// ── SIDEBAR ──
function updateSidebar(beat) {
  document.getElementById("arc-position-display").textContent =
    beat.arc_position.replace(/_/g, " ");
  document.getElementById("beat-title-display").textContent = beat.title;
  document.getElementById("char-state-display").textContent = beat.character_state;
  document.getElementById("world-state-display").textContent = beat.world_response;
}

function renderBeatsList(beats) {
  const list = document.getElementById("beats-completed");
  list.innerHTML = beats.map((b, i) =>
    `<div class="beat-item" id="beat-item-${i}">${b.title}</div>`
  ).join("");
}

function renderBeatProgress(activeIndex) {
  const prog = document.getElementById("beat-progress");
  prog.innerHTML = "";
  for (let i = 0; i < totalBeats; i++) {
    const dot = document.createElement("div");
    dot.className = "beat-dot" + (i < activeIndex ? " done" : i === activeIndex ? " active" : "");
    prog.appendChild(dot);
  }
}

// ── COMPLETE ──
async function showComplete() {
  try {
    const res = await fetch(`${API}/story/${sessionId}/state`);
    const state = await res.json();

    document.getElementById("complete-arc-title").textContent =
      state.skeleton.chosen_arc.title;

    const summary = document.getElementById("complete-summary");
    summary.innerHTML = state.scenes.map(s => `
      <div class="summary-beat">
        <strong>${s.beat.title}</strong>
        ${s.prose.substring(0, 200)}...
      </div>
    `).join("");

    showScreen("screen-complete");
  } catch (e) {
    showScreen("screen-complete");
  }
}

function startOver() {
  location.reload();
}

// ── UTILITIES ──
function showScreen(id) {
  document.querySelectorAll(".screen").forEach(s => s.classList.remove("active"));
  document.getElementById(id).classList.add("active");
  window.scrollTo(0, 0);
}

function showLoading(message = "Thinking...") {
  document.getElementById("loading-message").textContent = message;
  document.getElementById("loading").classList.remove("hidden");
}

function hideLoading() {
  document.getElementById("loading").classList.add("hidden");
}
