
import tkinter as tk
from tkinter import scrolledtext
import webbrowser
import subprocess
import os
import threading
import datetime
import time
import random
from urllib.parse import quote_plus

import sounddevice as sd
import speech_recognition as sr


# =============== SETTINGS ===============

SAMPLE_RATE = 16000
RECORD_SECONDS = 4

listening = threading.Event()
speaking_lock = threading.Lock()

root = tk.Tk()


# =============== GUI FUNCTIONS ===============

def add_message(sender, message):
    def update():
        try:
            chat_box.config(state="normal")
            chat_box.insert(tk.END, f"{sender}: {message}\n\n")
            chat_box.see(tk.END)
            chat_box.config(state="disabled")
        except tk.TclError:
            pass

    try:
        root.after(0, update)
    except RuntimeError:
        pass


def update_status(message):
    try:
        root.after(
            0, lambda: status_label.config(text=message)
        )
    except RuntimeError:
        pass


def update_buttons():
    try:
        listen_button.config(
            text="STOP LISTENING"
            if listening.is_set()
            else "START LISTENING"
        )
        status_label.config(
            text="Listening continuously..."
            if listening.is_set()
            else "Not listening"
        )
    except tk.TclError:
        pass


# =============== VOICE OUTPUT ===============

def speak(text):
    print("JARVIS:", text)
    add_message("JARVIS", text)

    safe_text = text.replace("'", "''")

    ps_command = (
        "Add-Type -AssemblyName System.Speech; "
        "$voice = New-Object "
        "System.Speech.Synthesis.SpeechSynthesizer; "
        f"$voice.Speak('{safe_text}')"
    )

    def run_voice():
        with speaking_lock:
            try:
                subprocess.run(
                    [
                        "powershell",
                        "-NoProfile",
                        "-Command",
                        ps_command
                    ],
                    capture_output=True,
                    timeout=30,
                    creationflags=getattr(
                        subprocess, "CREATE_NO_WINDOW", 0
                    )
                )
            except Exception as error:
                print("Voice error:", error)

    threading.Thread(target=run_voice, daemon=True).start()


# =============== GREETING ===============

def greet_user():
    hour = datetime.datetime.now().hour

    if hour < 12:
        greeting = "Good morning"
    elif hour < 17:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    replies = [
        f"{greeting}! I am Jarvis. How can I help you?",
        f"{greeting}! Your assistant is ready.",
        f"{greeting}! What can I do for you today?"
    ]

    speak(random.choice(replies))


# =============== GOOGLE SEARCH ===============

def google_search(query):
    query = query.strip()

    if not query:
        speak("Please tell me what you want to search.")
        return

    speak("Searching Google for " + query)

    url = (
        "https://www.google.com/search?q="
        + quote_plus(query)
    )

    webbrowser.open(url)


# =============== WEBSITE OPENING ===============

WEBSITES = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "gmail": "https://mail.google.com",
    "facebook": "https://www.facebook.com",
    "instagram": "https://www.instagram.com",
    "whatsapp": "https://web.whatsapp.com",
    "github": "https://github.com",
    "chatgpt": "https://chatgpt.com",
    "wikipedia": "https://www.wikipedia.org",
    "amazon": "https://www.amazon.in",
    "flipkart": "https://www.flipkart.com",
    "reddit": "https://www.reddit.com",
    "linkedin": "https://www.linkedin.com",
    "twitter": "https://x.com",
    "x": "https://x.com",
    "netflix": "https://www.netflix.com",
    "spotify": "https://open.spotify.com",
    "stackoverflow": "https://stackoverflow.com",
    "codeforces": "https://codeforces.com",
    "leetcode": "https://leetcode.com",
    "geeksforgeeks": "https://www.geeksforgeeks.org",
    "google drive": "https://drive.google.com",
    "google maps": "https://maps.google.com",
    "google classroom": "https://classroom.google.com"
}


def open_website(name):
    name = name.strip().lower()

    if not name:
        speak("Please tell me the website name.")
        return

    if name in WEBSITES:
        speak("Opening " + name)
        webbrowser.open(WEBSITES[name])
    else:
        # Search Google for an unfamiliar website
        google_search(name + " official website")


# =============== YOUTUBE SEARCH ===============

def youtube_search(query=""):
    query = query.strip()

    if query:
        speak("Searching YouTube for " + query)

        url = (
            "https://www.youtube.com/results?search_query="
            + quote_plus(query)
        )
    else:
        speak("Opening YouTube.")
        url = "https://www.youtube.com"

    webbrowser.open(url)


# =============== COMMAND HANDLER ===============

def handle_command(command):
    command = command.lower().strip()

    if not command:
        return

    add_message("YOU", command)
    print("Command:", command)

    # Stop listening
    if any(phrase in command for phrase in [
        "stop listening",
        "sleep jarvis",
        "go to sleep"
    ]):
        listening.clear()
        speak("Okay, I am stopping listening.")
        root.after(0, update_buttons)
        return

    # Greetings
    elif (
        command in ["hello", "hi", "hey"]
        or "hello jarvis" in command
        or "hi jarvis" in command
        or "hey jarvis" in command
        or "good morning" in command
        or "good afternoon" in command
        or "good evening" in command
    ):
        greet_user()

    elif "how are you" in command:
        speak("I am doing great. Thank you for asking!")

    elif "thank you" in command:
        speak("You're welcome. Happy to help.")

    elif "who are you" in command:
        speak("I am Jarvis, your personal voice assistant.")

    # YouTube commands
    elif "youtube" in command:
        query = command

        phrases = [
            "open youtube and play",
            "search youtube for",
            "search on youtube for",
            "play on youtube",
            "open youtube",
            "youtube",
            "search for",
            "please",
            "jarvis",
            "play",
            "search"
        ]

        for phrase in phrases:
            query = query.replace(phrase, " ").strip()

        youtube_search(query)

    # Google search commands
    elif command.startswith("google search for "):
        google_search(
            command.replace("google search for ", "", 1)
        )

    elif command.startswith("search google for "):
        google_search(
            command.replace("search google for ", "", 1)
        )

    elif command.startswith("search for "):
        google_search(
            command.replace("search for ", "", 1)
        )

    elif command.startswith("google "):
        google_search(command.replace("google ", "", 1))

    # Open a website
    elif command.startswith("open website "):
        open_website(
            command.replace("open website ", "", 1)
        )

    elif command.startswith("open site "):
        open_website(command.replace("open site ", "", 1))

    # Open apps, folders or websites
    elif command.startswith("open "):
        target = command.replace("open ", "", 1).strip()

        if target == "notepad":
            speak("Opening Notepad.")
            subprocess.Popen(["notepad.exe"])

        elif target in ["calculator", "calc"]:
            speak("Opening Calculator.")
            subprocess.Popen(["calc.exe"])

        elif target in ["file explorer", "explorer"]:
            speak("Opening File Explorer.")
            subprocess.Popen(["explorer.exe"])

        elif target == "downloads":
            speak("Opening Downloads.")
            os.startfile(
                os.path.join(
                    os.path.expanduser("~"), "Downloads"
                )
            )

        elif target == "documents":
            speak("Opening Documents.")
            os.startfile(
                os.path.join(
                    os.path.expanduser("~"), "Documents"
                )
            )

        else:
            open_website(target)

    # Play something on YouTube
    elif command.startswith("play "):
        youtube_search(command.replace("play ", "", 1))

    # Time and date
    elif "time" in command:
        now = datetime.datetime.now().strftime("%I:%M %p")
        speak("The time is " + now)

    elif "date" in command:
        today = datetime.datetime.now().strftime("%d %B %Y")
        speak("Today's date is " + today)

    else:
        speak(
            "Sorry, I did not understand. "
            "Try saying search for followed by your query."
        )


# =============== CONTINUOUS LISTENING ===============

def listening_loop():
    recognizer = sr.Recognizer()

    try:
        while listening.is_set():
            update_status("Listening...")

            audio = sd.rec(
                int(RECORD_SECONDS * SAMPLE_RATE),
                samplerate=SAMPLE_RATE,
                channels=1,
                dtype="int16"
            )
            sd.wait()

            if not listening.is_set():
                break

            audio_data = sr.AudioData(
                audio.tobytes(),
                SAMPLE_RATE,
                2
            )

            try:
                command = recognizer.recognize_google(
                    audio_data,
                    language="en-IN"
                )

                if command.strip():
                    handle_command(command)

            except sr.UnknownValueError:
                continue

            except sr.RequestError:
                update_status("Check internet connection")
                time.sleep(2)

    except Exception as error:
        print("Listening error:", error)
        update_status("Microphone error - check permissions")

    finally:
        listening.clear()
        root.after(0, update_buttons)


def start_listening():
    if listening.is_set():
        return

    listening.set()
    update_buttons()

    threading.Thread(
        target=listening_loop,
        daemon=True
    ).start()


def toggle_listening():
    if listening.is_set():
        listening.clear()
        update_buttons()
    else:
        start_listening()


def close_app():
    listening.clear()
    root.destroy()


# =============== GUI ===============

root.title("JARVIS - Voice Assistant")
root.geometry("680x620")
root.minsize(500, 450)
root.configure(bg="#101820")

tk.Label(
    root,
    text="J.A.R.V.I.S",
    font=("Consolas", 28, "bold"),
    fg="#00E5FF",
    bg="#101820"
).pack(pady=(20, 5))

tk.Label(
    root,
    text="YOUR PERSONAL VOICE ASSISTANT",
    font=("Consolas", 10),
    fg="white",
    bg="#101820"
).pack(pady=(0, 10))

status_label = tk.Label(
    root,
    text="Not listening",
    font=("Arial", 11),
    fg="#00E5FF",
    bg="#101820"
)
status_label.pack(pady=5)

chat_box = scrolledtext.ScrolledText(
    root,
    height=16,
    font=("Consolas", 10),
    bg="#17232D",
    fg="#EAFBFF",
    wrap=tk.WORD,
    state="disabled"
)
chat_box.pack(
    padx=20,
    pady=15,
    fill="both",
    expand=True
)

listen_button = tk.Button(
    root,
    text="START LISTENING",
    command=toggle_listening,
    font=("Arial", 12, "bold"),
    bg="#00B8D4",
    fg="black",
    activebackground="#00E5FF",
    relief="flat",
    padx=20,
    pady=12
)
listen_button.pack(pady=10)

tk.Label(
    root,
    text=(
        'Try: "Hello Jarvis", "Open Codeforces", '
        '"Search for Python tutorials", '
        '"Open YouTube Minecraft", "Stop listening".'
    ),
    font=("Arial", 9),
    fg="#B8C7CC",
    bg="#101820",
    wraplength=620
).pack(pady=(0, 15))

root.protocol("WM_DELETE_WINDOW", close_app)

add_message(
    "JARVIS",
    "Hello! Click START LISTENING to begin."
)

root.mainloop()
