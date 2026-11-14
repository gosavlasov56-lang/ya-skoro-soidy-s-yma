import json
import os
import random
import threading
import time
import tkinter as tk
from datetime import datetime

import requests
from gtts import gTTS
from PIL import Image, ImageTk
from playsound import playsound

NAME = "AIDA"
API_KEY = "AQ.Ab8RN6LWHrYk-qyqNcjasqd6Lp1bySO3szhceHfQIC2rGnbXsw"
AI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent"

# слова, за якими визначаємо емоцію
EMOTION_WORDS = {
    "laugh": ["жарт", "анекдот"],
    "happy": ["дякую", "супер", "привіт", "мотив"],
    "sad": ["помилка", "сумно"],
    "surprised": ["вау", "невже"],
    "thinking": ["чому", "що таке"],
    "angry": ["злий", "бісить"],
}
# колір фону для кожної емоції
COLORS = {
    "neutral": "#EEF2F7",
    "happy": "#FFF3C4",
    "laugh": "#FFE08A",
    "sad": "#DCE6F5",
    "surprised": "#FFE3CC",
    "thinking": "#EDE4FF",
    "angry": "#FADBD8",
}
JOKES = [
    "Чому програміст плутає Хелловін і Різдво? Бо 31 OCT = 25 DEC.",
    "Скільки програмістів треба, щоб замінити лампочку? Жодного — це апаратна проблема.",
]
MOTIVATION = [
    "Кожен баг — це крок до майстерності. Ти вже далеко пішов!",
    "Код не працює? Значить, ти за крок від того, щоб його виправити. Вперед!",
    "Великі проєкти починаються з одного рядка. Свій ти вже написав!",
]
QUICK_COMMANDS = {
    "Жарт": "Розкажи жарт",
    "Котра година": "Котра година?",
    "Мотивуй": "Мотивуй мене",
}
STOP_WORDS = ["стоп", "stop", "бувай", "до побачення"]

message_count = 0
current_emotion = "neutral"
lang = "uk"
last_error = ""


def say(text):
    # ділимо на речення
    text = text.replace("!", ".").replace("?", ".")
    for sentence in text.split("."):
        if sentence.strip() == "":
            continue
        try:
            gTTS(text=sentence, lang=lang).save("voice.mp3")
            playsound("voice.mp3")
            os.remove("voice.mp3")
        except Exception:
            pass
        time.sleep(0.3)  # пауза між реченнями


def say_async(text):
    threading.Thread(target=say, args=(text,), daemon=True).start()


def listen():
    try:
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
        if lang == "uk":
            return recognizer.recognize_google(audio, language="uk-UA")
        return recognizer.recognize_google(audio, language="en-US")
    except Exception:
        return ""


def ask_ai(question):
    global last_error
    if lang == "uk":
        language = "українською"
    else:
        language = "англійською"
    prompt = (
        f"Ти {NAME} — дружній голосовий асистент. Відповідай {language}, коротко: 1-3 речення. "
        "Відповідь буде озвучена вголос, тому пиши для озвучування: без markdown, списків, "
        "посилань та емодзі. "
        f"Поточна дата і час: {datetime.now():%d.%m.%Y %H:%M}."
    )
    try:
        response = requests.post(
            AI_URL,
            headers={"x-goog-api-key": API_KEY},
            json={
                "system_instruction": {"parts": [{"text": prompt}]},
                "contents": [{"role": "user", "parts": [{"text": question}]}],
            },
        )
        data = response.json()
        if "candidates" not in data:
            # Google повернув помилку — запам'ятовуємо її текст
            last_error = f"{response.status_code}: " + str(data.get("error", {}).get("message", data))[:200]
            return None
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as error:
        last_error = str(error)[:200]
        return None


def load_user_name():
    try:
        with open("user.json", encoding="utf-8") as f:
            return json.load(f).get("name")
    except Exception:
        return None


def save_user_name(name):
    with open("user.json", "w", encoding="utf-8") as f:
        json.dump({"name": name}, f, ensure_ascii=False)


def detect_emotion(text):
    text = text.lower()
    for emotion in EMOTION_WORDS:
        for word in EMOTION_WORDS[emotion]:
            if word in text:
                return emotion
    return "neutral"


def local_reply(text, emotion):
    text = text.lower()
    if emotion == "laugh":
        return random.choice(JOKES)
    if "годин" in text or "котра" in text:
        return "Зараз " + datetime.now().strftime("%H:%M")
    if "мотив" in text:
        return random.choice(MOTIVATION)
    return "Не вдалося отримати відповідь від нейромережі. Причина: " + last_error


def handle_command(text):
    global lang
    t = text.lower()
    if "англійською" in t:
        lang = "en"
        return "Okay, I will speak English now."
    if "українською" in t:
        lang = "uk"
        return "Добре, тепер говорю українською."
    if "мене звати" in t:
        words = t.split("мене звати")[1].split()
        if len(words) > 0:
            name = words[0].capitalize()
            save_user_name(name)
            return f"Приємно познайомитись, {name}!"
    return None


def set_emotion(emotion):
    global current_emotion
    current_emotion = emotion
    avatar.config(image=images[emotion])
    color = COLORS[emotion]
    root.configure(bg=color)
    avatar.config(bg=color)
    mood_label.config(bg=color, text=f"Настрій: {emotion}")


def update_title():
    root.title(f"{NAME} — {message_count} повідомлень")


def add_user(text):
    global message_count
    chat.config(state="normal")
    chat.insert(tk.END, f"Ти: {text}\n", "user")
    chat.config(state="disabled")
    chat.see(tk.END)
    message_count += 1
    update_title()


def add_bot(text):
    chat.config(state="normal")
    chat.insert(tk.END, f"{NAME}: {text}\n\n", "bot")
    chat.config(state="disabled")
    chat.see(tk.END)


def process(text):
    text = text.strip()
    if text == "":
        return

    if text.lower().strip(" .!?") in STOP_WORDS:
        farewell = "До зустрічі! Було приємно поговорити."
        add_user(text)
        add_bot(farewell)
        root.update()
        say(farewell)
        root.destroy()
        return

    add_user(text)

    command_reply = handle_command(text)
    if command_reply is not None:
        add_bot(command_reply)
        say_async(command_reply)
        return

    emotion = detect_emotion(text)
    set_emotion("thinking")
    mood_label.config(text="Думаю...")

    def work():
        answer = ask_ai(text)
        if answer is None:
            answer = local_reply(text, emotion)
        root.after(0, lambda: show_answer(answer, emotion))

    threading.Thread(target=work, daemon=True).start()


def show_answer(answer, emotion):
    add_bot(answer)
    set_emotion(emotion)
    say_async(answer)


def send(event=None):
    text = entry.get()
    entry.delete(0, tk.END)
    process(text)


def clear_chat():
    global message_count
    chat.config(state="normal")
    chat.delete("1.0", tk.END)
    chat.config(state="disabled")
    message_count = 0
    update_title()
    set_emotion("neutral")


def listen_click():
    # одна голосова фраза: слухаю -> відповідаю вголос
    mood_label.config(text="Слухаю...")

    def work():
        text = listen()
        root.after(0, lambda: after_listen(text))

    threading.Thread(target=work, daemon=True).start()


def after_listen(text):
    mood_label.config(text=f"Настрій: {current_emotion}")
    if text == "":
        add_bot("Я нічого не почула. Спробуй ще раз.")
    else:
        process(text)


def blink():
    avatar.config(image=images["blink"])
    root.after(150, unblink)


def unblink():
    avatar.config(image=images[current_emotion])
    root.after(random.randint(3000, 6000), blink)


root = tk.Tk()
root.geometry("520x680")
root.configure(bg=COLORS["neutral"])
update_title()

images = {}
for name in list(COLORS) + ["blink"]:
    picture = Image.open(f"avatars/{name}.png").resize((180, 180))
    images[name] = ImageTk.PhotoImage(picture)

avatar = tk.Label(root, image=images["neutral"], bg=COLORS["neutral"])
avatar.pack(pady=(15, 0))
mood_label = tk.Label(root, text="Настрій: neutral", font=("Arial", 10), bg=COLORS["neutral"], fg="#5F6B7A")
mood_label.pack()

chat = tk.Text(root, height=14, width=56, wrap="word", font=("Arial", 11), state="disabled", relief="flat",
               padx=8, pady=8)
chat.tag_config("user", foreground="#2F6FB5")
chat.tag_config("bot", foreground="#1F2933")
chat.pack(padx=15, pady=10)

quick = tk.Frame(root)
quick.pack(fill="x", padx=15)
for label in QUICK_COMMANDS:
    tk.Button(quick, text=label, relief="flat", bg="#FFFFFF", padx=8,
              command=lambda t=QUICK_COMMANDS[label]: process(t)).pack(side="left", padx=(0, 6))
tk.Button(quick, text="Очистити чат", relief="flat", bg="#FFFFFF", fg="#B3261E", padx=8,
          command=clear_chat).pack(side="right")

# поле введення
bottom = tk.Frame(root, bg="#FFFFFF")
bottom.pack(fill="x", padx=15, pady=15)
entry = tk.Entry(bottom, font=("Arial", 12), relief="flat")
entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(6, 0))
entry.bind("<Return>", send)
tk.Button(bottom, text="Надіслати", command=send, bg="#FF9C00", fg="white", relief="flat",
          padx=10).pack(side="right", padx=4, pady=4)
tk.Button(bottom, text="Mік.", command=listen_click, relief="flat", padx=6).pack(side="right", pady=4)
entry.focus()

user_name = load_user_name()
if user_name:
    greeting = f"Привіт, {user_name}! Я {NAME}, твій помічник."
else:
    greeting = f"Привіт! Я {NAME}, твій помічник."
add_bot(greeting)
say_async(greeting)

root.after(4000, blink)
root.mainloop()
