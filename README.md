# AuraSight - Voice & Vision Assistant

AuraSight is a modern desktop assistant that combines computer vision and voice interaction. It uses your webcam to capture images, listens to your voice commands, and responds using AI-powered language and speech synthesis.

---

## Features

- **Voice-activated commands**: Just say "start", "stop", "follow up", "clear history", "ok", or "restart"—no button clicks needed!
- **Image capture**: Takes a photo using your webcam.
- **Speech-to-text**: Converts your spoken questions into text.
- **AI-powered answers**: Uses a Cohere Multimodal LLM to answer your questions about the scene or follow up.
- **Text-to-speech**: Speaks the AI's answer back to you.
- **Modern Tkinter GUI**: Clean, accessible interface.

---

## Environment Setup

It is recommended to use a Python virtual environment to keep dependencies isolated.

### 1. Create and Activate a Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 2. Install Requirements

All dependencies are listed in `requirements.txt`.  
Install them with:

```bash
pip install -r requirements.txt
```

**Example `requirements.txt`:**
```
simpleaudio
Pillow
opencv-python
SpeechRecognition
pyaudio
cohere
```

---

### 3. Cohere Multimodal Setup

AuraSight uses [Cohere's Multimodal API](https://docs.cohere.com/docs/multimodal-overview) for vision-language understanding.

- **Sign up at [Cohere](https://dashboard.cohere.com/) and get your API key.**
- Set your API key as an environment variable before running the app:

**Windows:**
```powershell
set COHERE_API_KEY=your-api-key-here
```

**macOS/Linux:**
```bash
export COHERE_API_KEY=your-api-key-here
```

- The app expects your `utils/llm.py` to use this environment variable to authenticate.

---

## Usage

1. **Run the app:**
    ```bash
    python main.py
    ```

2. **Voice commands:**
    - `"start"`: Capture an image and ask a question.
    - `"stop"`: Stop recording.
    - `"follow up"`: Ask a follow-up question.
    - `"clear history"`: Clear conversation history.
    - `"ok"`: End session and disable buttons.
    - `"restart"`: Re-enable all buttons.

3. **Buttons:**  
   You can also use the on-screen buttons for all actions.

---

## Project Structure

```
AuraSight/
├── main.py
├── requirements.txt
├── utils/
│   ├── camera.py
│   ├── llm.py
│   ├── mic_input.py
│   ├── stt.py
│   └── text_to_speech.py
└── README.md
```

---

## Notes

- Make sure your microphone and webcam are connected and accessible.
- The app uses Google Speech Recognition for STT by default.
- For LLM features, configure your Cohere API key as described above.

---

## License

MIT License

---

**Enjoy using AuraSight!**