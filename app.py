import os
import time
import tempfile
import speech_recognition as sr
import openai
from flask import Flask, render_template, request, jsonify
from gtts import gTTS
from pydub import AudioSegment
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime

app = Flask(__name__)

# ---------------- FFmpeg ----------------
ffmpeg_path = r"C:\Users\ABC\Downloads\ffmpeg-8.0-essentials_build\ffmpeg-8.0-essentials_build\bin\ffmpeg.exe"
AudioSegment.converter = ffmpeg_path

# ---------------- Firebase ----------------
cred = credentials.Certificate(r"C:\\GPT\\voice_teacher_web\\aivoiceteacher-firebase-adminsdk-fbsvc-43a0096c8a.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://aivoiceteacher-default-rtdb.firebaseio.com/'
})

# ---------------- OpenAI Azure ----------------
openai.api_type = "azure"
openai.api_base = "API BASE"
openai.api_version = "VERSION"
openai.api_key = "YOUR API KEY"

# ---------------- Recognizer ----------------
recognizer = sr.Recognizer()

# ---------------- Audio Folder ----------------
# AUDIO_FOLDER = os.path.join("static", "audio")
# os.makedirs(AUDIO_FOLDER, exist_ok=True)

AUDIO_FOLDER = os.path.join(app.root_path, "static", "audio")
os.makedirs(AUDIO_FOLDER, exist_ok=True)


# ---------------- License ----------------
def check_license():
    try:
        ref = db.reference("license")
        data = ref.get()
        expiry = data.get("expiry_date")
        expiry_date = datetime.strptime(expiry, "%Y-%m-%d")
        if datetime.now() > expiry_date:
            return False, f"License expired on {expiry_date.date()}"
        return True, f"Valid till {expiry_date.date()}"
    except Exception as e:
        return False, f"License check failed: {e}"

# ---------------- Routes ----------------
@app.route("/")
def index():
    ok, msg = check_license()
    if not ok:
        return f"<h2 style='color:red;'>⛔ {msg}</h2>"
    return render_template("index.html")


@app.route("/process_audio", methods=["POST"])
def process_audio():
    ok, msg = check_license()
    if not ok:
        return jsonify({"error": msg}), 403

    try:
        audio_file = request.files.get("audio_data")
        if not audio_file:
            return jsonify({"error": "No audio file"}), 400

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav:
            AudioSegment.from_file(audio_file).export(temp_wav.name, format="wav")

        # Speech Recognition
        with sr.AudioFile(temp_wav.name) as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.4)
            audio = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio, language="ta-IN")
            except sr.UnknownValueError:
                text = ""
        os.remove(temp_wav.name)

        if not text.strip():
            return jsonify({"status": "no_speech"})

        print("🎧 Heard:", text)

        # Detect Tamil or English
        is_tamil = any('\u0B80' <= ch <= '\u0BFF' for ch in text)

        # AI Prompt
        prompt = f"""
You are "Eniya Sri", a bilingual Tamil + English teacher.
- Reply in Tamil if question is in Tamil, unless user asks for English.
- Reply in English if question is in English, unless user asks for Tamil.
- Explain grammar, meanings, or math formulas clearly in 2–3 lines max.

Student: {text}
Teacher:
"""
        response = openai.ChatCompletion.create(
            deployment_id="gpt-4o-2024-08-06",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.6
        )
        reply = response["choices"][0]["message"]["content"].strip()
        print("🧠 Reply:", reply)

        # ---------------- Clear old TTS ----------------
        for f in os.listdir(AUDIO_FOLDER):
            if f.endswith(".mp3"):
                try:
                    os.remove(os.path.join(AUDIO_FOLDER, f))
                except:
                    pass

        # ---------------- Save new TTS ----------------
        tts_filename = f"response_{int(time.time()*1000)}.mp3"
        tts_path = os.path.join(AUDIO_FOLDER, tts_filename)
        tts_lang = "ta" if any('\u0B80' <= ch <= '\u0BFF' for ch in reply) else "en"
        gTTS(text=reply, lang=tts_lang, tld='co.in').save(tts_path)

        # ---------------- Return proper URL ----------------
        audio_url = f"/static/audio/{tts_filename}"

        return jsonify({
            "text": text,
            "response": reply,
            "audio_url": audio_url
        })

    except Exception as e:
        print("❌", e)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("🚀 Tamil+English AI Voice Teacher running at http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
