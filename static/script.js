const conversationContainer = document.getElementById("conversation-container");
const statusText = document.getElementById("status-text");

let isSpeaking = false;

window.onload = () => {
  startListening();
};

function startListening() {
  navigator.mediaDevices.getUserMedia({ audio: true })
    .then(stream => {
      const recorder = new MediaRecorder(stream);
      let chunks = [];

      recorder.ondataavailable = e => chunks.push(e.data);
      recorder.onstop = () => {
        const audioBlob = new Blob(chunks, { type: 'audio/webm' });
        chunks = [];
        processAudio(audioBlob);
      };

      const listenLoop = () => {
        if (!isSpeaking) {
          statusText.textContent = "🎤 Listening... Speak your question.";
          recorder.start();

          // Stop when silent for 2s
          setTimeout(() => {
            if (recorder.state === "recording") {
              recorder.stop();
            }
          }, 7000);
        }
      };

      listenLoop();
      window.listenLoop = listenLoop;
    })
    .catch(() => statusText.textContent = "⚠️ Microphone access denied.");
}

function processAudio(blob) {
  statusText.textContent = "⏳ Processing...";
  const form = new FormData();
  form.append("audio_data", blob);

  fetch("/process_audio", { method: "POST", body: form })
    .then(res => res.json())
    .then(data => {
      if (data.status === "no_speech") {
        statusText.textContent = "🎤 Speak again...";
        setTimeout(window.listenLoop, 1500);
        return;
      }

      if (data.error) {
        showMessage("❌ " + data.error);
        statusText.textContent = "🎤 Ready again...";
        setTimeout(window.listenLoop, 1500);
        return;
      }

      showMessage(`👤 ${data.text}<br><br>🧠 ${data.response}`);

      if (data.audio_url) {
        const audio = new Audio(data.audio_url);
        isSpeaking = true;
        statusText.textContent = "🔊 Speaking...";
        audio.play();
        audio.onended = () => {
          isSpeaking = false;
          setTimeout(window.listenLoop, 800);
        };
      } else {
        setTimeout(window.listenLoop, 1000);
      }
    })
    .catch(err => {
      console.error(err);
      statusText.textContent = "⚠️ Error, retrying...";
      setTimeout(window.listenLoop, 1500);
    });
}

function showMessage(text) {
  conversationContainer.innerHTML = "";
  const div = document.createElement("div");
  div.classList.add("message");
  div.innerHTML = text;
  conversationContainer.appendChild(div);
}
