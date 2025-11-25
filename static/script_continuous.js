const socket = io();
const chatBox = document.getElementById("chat-box");
const statusEl = document.getElementById("status");

let listening = false;
let stopped = false;

socket.on("message", (data) => {
    const msgDiv = document.createElement("div");
    msgDiv.classList.add("message", data.speaker);
    msgDiv.textContent = `${data.speaker}: ${data.text}`;
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
});

socket.on("status", (data) => {
    statusEl.textContent = "Status: " + data.status;
});

socket.on("play_audio", async (data) => {
    statusEl.textContent = "Speaking...";
    const audio = new Audio(data.url);
    audio.onended = () => {
        if (!stopped) startListening();
    };
    audio.play();
});

async function startWakeWordListening() {
    stopped = false;
    statusEl.textContent = "Say 'Hi Teacher' or 'Ava' to start...";
    while (!stopped) {
        const text = await recognizeSpeech(4000);
        if (text && (text.toLowerCase().includes("hi teacher") || text.toLowerCase().includes("ava"))) {
            socket.emit("message", { speaker: "Teacher", text: "Hello! I'm Ava, your teacher. What can I help you with?" });
            startListening();
            break;
        }
    }
}

async function startListening() {
    if (listening) return;
    listening = true;
    statusEl.textContent = "Listening for your question...";
    while (!stopped) {
        const text = await recognizeSpeech(8000);
        if (!text) continue;

        socket.emit("message", { speaker: "Student", text });

        if (["thank you", "thanks", "bye", "goodbye"].some(w => text.toLowerCase().includes(w))) {
            socket.emit("message", { speaker: "Teacher", text: "You're welcome! Returning to standby mode." });
            stopped = true;
            listening = false;
            startWakeWordListening();
            break;
        }

        const blob = await recordAudioBlob(4000);
        socket.emit("audio_data", blob);
    }
}

async function recognizeSpeech(duration) {
    return new Promise(async (resolve) => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const recorder = new MediaRecorder(stream);
            let chunks = [];
            recorder.ondataavailable = (e) => chunks.push(e.data);
            recorder.onstop = async () => {
                const blob = new Blob(chunks, { type: "audio/webm" });
                socket.emit("audio_data", blob);
            };
            recorder.start();
            setTimeout(() => recorder.stop(), duration);
        } catch (err) {
            console.error(err);
            resolve("");
        }
    });
}

startWakeWordListening();
