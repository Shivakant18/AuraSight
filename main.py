import tkinter as tk
import threading
import simpleaudio as sa
from PIL import Image, ImageTk
import cv2
import speech_recognition as sr

# Your utility imports
from utils.camera import capture_image_pil
from utils.llm import summarize_scenary, answer_question, ask_followup, clear_history
from utils.text_to_speech import generate_voice
from utils.mic_input import record_audio
from utils.stt import transcribe_audio_to_text

# Globals
recording = False
record_duration = 5  # seconds
image_display = None  # store latest image for UI
image_label = None    # tkinter label to hold image
current_play_obj = None  # store current TTS playback object
recording_event = threading.Event()

# === Update image in UI ===
def update_display_image(pil_img):
    global image_display
    img_resized = pil_img.resize((300, 300), Image.Resampling.LANCZOS)
    image_display = ImageTk.PhotoImage(img_resized)
    image_label.configure(image=image_display)

def on_playback_done():
    global current_play_obj
    current_play_obj = None
    status_label.config(text="Done.")

def play_audio_non_blocking(wave_obj):
    global current_play_obj
    current_play_obj = wave_obj.play()
    def wait_and_finish():
        current_play_obj.wait_done()
        root.after(0, on_playback_done)
    threading.Thread(target=wait_and_finish, daemon=True).start()

def handle_start():
    def task():
        global recording, current_play_obj
        recording = True
        recording_event.set()
        status_label.config(text="Capturing image...")
        try:
            image = capture_image_pil()
            update_display_image(image)
            status_label.config(text="Recording voice...")
            audio_file = record_audio(duration=record_duration)
        except Exception as e:
            status_label.config(text="Failed.")
            tk.messagebox.showerror("Error", f"Error: {e}")
            recording_event.clear()
            return
        status_label.config(text="Thinking...")
        try:
            question = transcribe_audio_to_text(audio_file)
            if len(question) > 0:
                summary = answer_question(image, question)
            else:
                summary = summarize_scenary(image)
        except Exception as e:
            tk.messagebox.showerror("Error", f"LLM failed: {e}")
            status_label.config(text="LLM failed")
            return
        try:
            file_path = generate_voice(summary)
            wave_obj = sa.WaveObject.from_wave_file(file_path)
            status_label.config(text="Playing response...")
            play_audio_non_blocking(wave_obj)
        except Exception as e:
            tk.messagebox.showerror("Error", f"TTS failed: {e}")
            return
        recording = False
        recording_event.clear()
    threading.Thread(target=task).start()

def handle_stop():
    global recording
    recording = False
    status_label.config(text="Stopped recording.")

def history_clear():
    def task():
        clear_history()
        status_label.config(text="History cleared.")
    threading.Thread(target=task).start()

def handle_off():
    global recording, current_play_obj
    recording = False
    status_label.config(text="Session ended. All actions stopped.")
    # Stop TTS playback if running
    if current_play_obj is not None:
        try:
            current_play_obj.stop()
        except Exception:
            pass
        current_play_obj = None
    # Disable all action buttons
    start_btn.config(state="disabled")
    stop_btn.config(state="disabled")
    followup_btn.config(state="disabled")
    clearHistory_btn.config(state="disabled")
    off_btn.config(state="disabled")

def handle_restart():
    # Re-enable all action buttons
    start_btn.config(state="normal")
    stop_btn.config(state="normal")
    followup_btn.config(state="normal")
    clearHistory_btn.config(state="normal")
    off_btn.config(state="normal")
    status_label.config(text="Idle")

def followup():
    def task():
        global recording, current_play_obj
        recording = True
        recording_event.set()
        status_label.config(text="Recording voice...")
        try:
            audio_file = record_audio(duration=record_duration)
        except Exception as e:
            status_label.config(text="Failed.")
            tk.messagebox.showerror("Error", f"Error: {e}")
            recording_event.clear()
            return
        status_label.config(text="Thinking...")
        try:
            question = transcribe_audio_to_text(audio_file)
            if len(question) > 0:
                answer = ask_followup(question)
            else:
                answer = ""
        except Exception as e:
            tk.messagebox.showerror("Error", f"LLM Failed: {e}")
            return
        try:
            file_path = generate_voice(answer)
            wave_obj = sa.WaveObject.from_wave_file(file_path)
            status_label.config(text="Playing response...")
            play_audio_non_blocking(wave_obj)
        except Exception as e:
            tk.messagebox.showerror("Error", f"TTS failed: {e}")
            return
        recording = False
        recording_event.clear()
    threading.Thread(target=task).start()

# Window setup
root = tk.Tk()
root.title("🕶 AuraSight - Voice & Vision Assistant")
root.geometry("700x400")
root.configure(bg="#121212")

# Colors & Style
CYAN = "#00bcd4"
CYAN_DARK = "#0097a7"
WHITE = "#ffffff"
DARK_BG = "#181c20"
CARD_BG = "#23272b"
SHADOW = "#0a0c0e"
ACCENT = "#ffb300"
FONT = ("Segoe UI Semibold", 13)
TITLE_FONT = ("Segoe UI Black", 18, "bold")
BUTTON_WIDTH = 20
BUTTON_HEIGHT = 2
BUTTON_STYLE = {
    "font": FONT,
    "width": BUTTON_WIDTH,
    "height": BUTTON_HEIGHT,
    "bd": 0,
    "relief": "flat",
    "bg": CYAN,
    "fg": WHITE,
    "activebackground": CYAN_DARK,
    "activeforeground": WHITE,
    "cursor": "hand2",
    "highlightthickness": 2,
    "highlightbackground": CYAN_DARK,
    "highlightcolor": CYAN_DARK
}

# --- Custom hover effect for buttons ---
def on_enter(e):
    e.widget["bg"] = ACCENT
    e.widget["fg"] = DARK_BG

def on_leave(e):
    e.widget["bg"] = CYAN
    e.widget["fg"] = WHITE

# === LAYOUT: Modernized ===
main_frame = tk.Frame(root, bg=DARK_BG)
main_frame.pack(expand=True, fill="both", padx=20, pady=20)

# --- Title Bar ---
title_bar = tk.Frame(main_frame, bg=DARK_BG)
title_bar.pack(fill="x", pady=(0, 10))
title_label = tk.Label(title_bar, text="🕶 AuraSight", font=TITLE_FONT, bg=DARK_BG, fg=CYAN, anchor="w")
title_label.pack(side="left", padx=(10, 0))
subtitle_label = tk.Label(title_bar, text="Voice & Vision Assistant", font=("Segoe UI", 12), bg=DARK_BG, fg="#bbbbbb", anchor="w")
subtitle_label.pack(side="left", padx=(10, 0))

# --- LEFT: Image Card ---
card_shadow_img = tk.Frame(main_frame, bg=SHADOW, width=340, height=340)
card_shadow_img.pack_propagate(False)
card_shadow_img.pack(side="left", fill="both", expand=False, padx=(0, 18), pady=10)
image_card = tk.Frame(card_shadow_img, bg=CARD_BG, width=320, height=320, bd=0, relief="ridge", highlightthickness=2, highlightbackground=CYAN)
image_card.pack(expand=True, fill="both", padx=10, pady=10)
image_label = tk.Label(image_card, bg=CARD_BG)
image_label.pack(expand=True, padx=10, pady=10)

# --- RIGHT: Buttons Card ---
card_shadow_btn = tk.Frame(main_frame, bg=SHADOW, width=220)
card_shadow_btn.pack_propagate(False)
card_shadow_btn.pack(side="right", fill="y", padx=(0, 0), pady=10)
button_card = tk.Frame(card_shadow_btn, bg=CARD_BG, width=200, bd=0, relief="ridge", highlightthickness=2, highlightbackground=CYAN_DARK)
button_card.pack(expand=True, fill="y", padx=10, pady=10)

# --- Buttons ---
start_btn = tk.Button(button_card, text="Start", command=handle_start, **BUTTON_STYLE)
start_btn.pack(pady=(0, 8), fill="x")
start_btn.bind("<Enter>", on_enter)
start_btn.bind("<Leave>", on_leave)

stop_btn = tk.Button(button_card, text="Stop", command=handle_stop, **BUTTON_STYLE)
stop_btn.pack(pady=8, fill="x")
stop_btn.bind("<Enter>", on_enter)
stop_btn.bind("<Leave>", on_leave)

followup_btn = tk.Button(button_card, text="Follow Up", command=followup, **BUTTON_STYLE)
followup_btn.pack(pady=8, fill="x")
followup_btn.bind("<Enter>", on_enter)
followup_btn.bind("<Leave>", on_leave)

clearHistory_btn = tk.Button(button_card, text="Clear History", command=history_clear, **BUTTON_STYLE)
clearHistory_btn.pack(pady=8, fill="x")
clearHistory_btn.bind("<Enter>", on_enter)
clearHistory_btn.bind("<Leave>", on_leave)

off_btn = tk.Button(button_card, text="OK", command=handle_off, **BUTTON_STYLE)
off_btn.pack(pady=8, fill="x")
off_btn.bind("<Enter>", on_enter)
off_btn.bind("<Leave>", on_leave)

restart_btn = tk.Button(button_card, text="Restart", command=handle_restart, **BUTTON_STYLE)
restart_btn.pack(pady=8, fill="x")
restart_btn.bind("<Enter>", on_enter)
restart_btn.bind("<Leave>", on_leave)

# --- Separator ---
tk.Frame(button_card, height=2, bg=CYAN_DARK).pack(fill="x", pady=10)

status_label = tk.Label(button_card, text="Idle", font=("Segoe UI", 12, "italic"),
                        bg=CARD_BG, fg="#dddddd", anchor="center", wraplength=180, bd=0, relief="flat")
status_label.pack(pady=12, padx=8, fill="x")

def voice_command_listener():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    commands = {
        "start": handle_start,
        "stop": handle_stop,
        "follow up": followup,
        "clear history": history_clear,
        "ok": handle_off,  # Changed from "off" to "ok"
        "restart": handle_restart
    }
    while True:
        # Wait if recording_event is set (i.e., app is recording)
        if recording_event.is_set():
            threading.Event().wait(0.5)
            continue
        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
            try:
                audio = recognizer.listen(source, timeout=5)
                text = recognizer.recognize_google(audio).lower()
                print(f"Voice command: {text}")
                for cmd, func in commands.items():
                    if cmd in text:
                        root.after(0, func)
                        break
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                continue
            except Exception as e:
                print(f"Voice command error: {e}")

# Start voice command listener in a background thread
threading.Thread(target=voice_command_listener, daemon=True).start()

root.mainloop()