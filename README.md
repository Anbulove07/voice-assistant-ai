# AI Voice Assistant Teacher (English + Tamil)  
Python | Google Speech Recognition | GPT API | Offline/Online Hybrid

---

## ⭐ Project Overview
The **AI Voice Assistant Teacher** is an interactive voice-based learning system designed to help users improve English communication, vocabulary, grammar, and pronunciation.  
It listens to commands, understands natural language, and responds with human-like explanations using GPT API.

It supports:
- **Google Speech Recognition** (online)
- **Vosk** (offline speech recognition)
- **GPT API** for intelligent responses
- **pyttsx3 / gTTS** for text-to-speech
- Optional **Flask Web UI** for browser-based interaction

Compatible with **Windows, Linux, and Raspberry Pi**.

---

## 🎯 Key Features

### 🔊 Voice Interaction
- Wake word activation (e.g., “Hello Teacher”)  
- Continuous listening mode  
- Optional LED indicators for Raspberry Pi  

### 🎤 Speech Recognition
- **Online:** Google Speech Recognition API  
- **Offline:** Vosk Model (fallback when no internet)  
- Automatic network-based switching  

### 🧠 GPT-Powered Teaching
- Grammar explanation  
- Sentence construction (present, past, future tenses)  
- Vocabulary learning  
- Sentence correction  
- Translation (Tamil ↔ English)  
- Answering general knowledge questions  

### 🔈 Voice Output
- **Online:** gTTS (Google Text-to-Speech)  
- **Offline:** pyttsx3 / Piper  


### 🖥️ Optional Web Dashboard
- Record voice commands  
- View logs and responses  
- Manage settings  
- Accessible at `http://localhost:5000`

---

## 🛠️ Tech Stack

**Languages:** Python 3.x  
**Speech Recognition:** Google Speech Recognition, Vosk  
**NLP / LLM:** OpenAI GPT API  
**Text-to-Speech:** gTTS, pyttsx3, Piper  
**Frameworks / Libraries:** Flask, SpeechRecognition, pyaudio, numpy, sounddevice, GPIO Zero (Raspberry Pi)  

---


