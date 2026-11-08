import json
import os
from datetime import datetime

import requests
import speech_recognition as sr

API_KEY = os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6Kta_aIKfImqIiMyP4Vn7BVRaLeinTFfNuINHsaB8Ainw")

URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"


def ask_ai(messages):
    try:
        history = []
        for m in messages[1:]:
            role = "model" if m["role"] == "assistant" else "user"
            history.append({"role": role, "parts": [{"text": m["content"]}]})
        r = requests.post(
            URL,
            headers={"x-goog-api-key": API_KEY},
            json={
                "system_instruction": {"parts": [{"text": messages[0]["content"]}]},
                "contents": history,
            },
            timeout=30,
        )
        data = r.json()
        if "candidates" not in data:
            print("[API]", data.get("error", {}).get("message", data))
            return None
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print("[Помилка запиту]", e)
        return None


try:
    with open("user.json", encoding="utf-8") as f:
        NAME = json.load(f)["name"]
except Exception:
    NAME = "друже"

RULES = " Відповідай українською і коротко. Не вигадуй факти. Пам'ятай розмову."
PERSONAS = {
    "вчитель": "Ти Біт, добрий вчитель. Пояснюєш просто.",
    "радник": "Ти Біт, чіткий радник. Даєш поради кроками.",
}
mode = "вчитель"


def system():
    return {"role": "system", "content": PERSONAS[mode] + RULES + " Користувача звати " + NAME}


messages = [system()]


def chat(text):
    messages.append({"role": "user", "content": text})
    recent = messages[1:][-20:]
    while recent and recent[0]["role"] != "user":  # історія має починатися з user
        recent.pop(0)
    answer = ask_ai([messages[0]] + recent)
    if answer is None:
        messages.pop()
        return "Помилка зв'язку"
    messages.append({"role": "assistant", "content": answer})
    return answer


def listen():
    r = sr.Recognizer()
    try:
        with sr.Microphone() as s:
            r.adjust_for_ambient_noise(s, duration=0.5)
            print("[Слухаю...]")
            audio = r.listen(s, timeout=5, phrase_time_limit=7)
        return r.recognize_google(audio, language="uk-UA")
    except sr.WaitTimeoutError:
        print("[Тихо]")
    except sr.UnknownValueError:
        print("[Не розібрав]")
    except sr.RequestError:
        print("[Немає інтернету]")
    except (OSError, AttributeError):  # немає мікрофона або PyAudio
        return input("Ти: ")
    return ""


def normalize(text):
    t = text.lower().strip()
    for ch in ("’", "ʼ", "`"):
        t = t.replace(ch, "'")
    return t.rstrip(".!?, ")


ok = 0
bad = 0
while True:
    text = listen()
    if text == "":
        bad += 1
        continue
    ok += 1
    print("Ти сказав:", text)
    with open("log_speech.txt", "a", encoding="utf-8") as f:
        f.write(str(datetime.now()) + " | " + text + "\n")
    t = normalize(text)

    if t == "стоп":
        print("Біт: Тримай ритм!")
        print("Розпізнано:", ok, "Не розпізнано:", bad)
        break
    elif t == "очисти пам'ять":
        messages[:] = [system()]
        print("Біт: Пам'ять очищено!")
    elif t in ("режим вчитель", "режим радник"):
        mode = t.split()[1]
        messages[:] = [system()]
        print("Біт: Режим", mode)
    elif t == "скільки повідомлень":
        print("Біт:", len(messages) - 1)
    elif t == "що я казав":
        with open("log_speech.txt", encoding="utf-8") as f:
            for line in f.readlines()[-3:]:
                print("  ", line.strip())
    elif "привіт" in t:
        print("Біт: Привіт,", NAME + "!")
    elif "котра година" in t:
        print("Біт: Зараз", datetime.now().strftime("%H:%M"))
    elif "жарт" in t:
        print("Біт: Oct 31 == Dec 25!")
    else:
        print("Біт:", chat(text))
