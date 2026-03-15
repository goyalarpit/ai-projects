const API_URL = "http://localhost:8000";

// ── Screen management ──
function showScreen(id) {
  document.querySelectorAll(".screen").forEach(s => s.classList.remove("active"));
  document.getElementById(id).classList.add("active");
}

// ── Timer ──
let timerInterval = null;
let secondsLeft   = 30;

function startTimer() {
  secondsLeft = 30;
  updateTimerDisplay();
  timerInterval = setInterval(() => {
    secondsLeft--;
    updateTimerDisplay();
    if (secondsLeft <= 0) {
      clearInterval(timerInterval);
      document.getElementById("btn-done").style.display = "inline-block";
      document.getElementById("record-prompt").textContent = "Ready when you are.";
    }
  }, 1000);
}

function updateTimerDisplay() {
  const m = Math.floor(secondsLeft / 60);
  const s = secondsLeft % 60;
  document.getElementById("timer").textContent = `${m}:${s.toString().padStart(2, "0")}`;
}

// ── Voice recording ──
let mediaRecorder = null;
let audioChunks   = [];
let transcript    = "";

async function startRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    audioChunks  = [];
    mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.ondataavailable = e => {
      if (e.data.size > 0) audioChunks.push(e.data);
    };

    mediaRecorder.onstop = () => {
      stream.getTracks().forEach(t => t.stop());
      // For now, use a mock transcript since Whisper isn't integrated yet
      // In production: send audioBlob to Whisper API here
      transcript = getMockTranscriptFromPrompt();
      processTranscript(transcript);
    };

    mediaRecorder.start();
    startTimer();
    showScreen("screen-record");
  } catch (err) {
    alert("Microphone access is needed. Please allow microphone and try again.");
  }
}

function stopRecording() {
  clearInterval(timerInterval);
  if (mediaRecorder && mediaRecorder.state !== "inactive") {
    mediaRecorder.stop();
  }
  showScreen("screen-processing");
}

// Temporary: returns a mock transcript to test the full flow
// until Whisper voice transcription is integrated
function getMockTranscriptFromPrompt() {
  return "I've just had such a long day. Work was really stressful, " +
         "I couldn't focus on anything and my mind keeps racing. " +
         "I feel tense and I just can't seem to switch off.";
}

// ── API call ──
async function processTranscript(text) {
  try {
    const res = await fetch(`${API_URL}/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ transcript: text }),
    });

    if (!res.ok) throw new Error(`API error: ${res.status}`);

    const data = await res.json();
    renderPlaylist(data);
    showScreen("screen-playlist");
  } catch (err) {
    console.error(err);
    alert("Something went wrong. Please try again.");
    showScreen("screen-welcome");
  }
}

// ── Render playlist ──
function renderPlaylist(data) {
  const { user_mood, journey } = data;

  document.getElementById("mood-summary").textContent = user_mood.summary;

  const container = document.getElementById("phases-container");
  container.innerHTML = "";

  journey.forEach(phase => {
    const block = document.createElement("div");
    block.className = "phase-block";

    const label = document.createElement("div");
    label.className = "phase-label";
    label.textContent = `Phase ${phase.phase} — ${phase.label}`;
    block.appendChild(label);

    phase.tracks.forEach(track => {
      const item = document.createElement("div");
      item.className = "track-item";
      item.innerHTML = `
        <div class="track-info">
          <div class="track-title">${escapeHtml(track.title)}</div>
          <div class="track-artist">${escapeHtml(track.artist)}</div>
        </div>
        <div class="track-duration">${track.duration}</div>
        <a class="track-play" href="${track.spotify.web}" target="_blank">
          &#9654; Spotify
        </a>
      `;
      block.appendChild(item);
    });

    container.appendChild(block);
  });
}

function escapeHtml(str) {
  return str.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
}

// ── Event listeners ──
document.getElementById("btn-start").addEventListener("click", startRecording);

document.getElementById("btn-done").addEventListener("click", stopRecording);

document.getElementById("btn-cancel").addEventListener("click", () => {
  clearInterval(timerInterval);
  if (mediaRecorder && mediaRecorder.state !== "inactive") {
    mediaRecorder.stream?.getTracks().forEach(t => t.stop());
    mediaRecorder.stop();
  }
  showScreen("screen-welcome");
});

document.getElementById("btn-restart").addEventListener("click", () => {
  showScreen("screen-welcome");
});
