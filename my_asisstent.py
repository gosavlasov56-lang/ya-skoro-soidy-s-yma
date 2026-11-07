import json
from datetime import datetime
import speech_recognition as sr


def ask_ai(messages):
    try:
        history = []
        for m in messages[1:]:
            role = "model" if m["role"] == "assistant" else "user"
            history.append({"role": role, "parts": [{"text": m["content"]}]})
        r = requests.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
            params={"key": AQ.Ab8RN6Kta_aIKfImqIiMyP4Vn7BVRaLeinTFfNuINHsaB8Ainw},
            json={
                "system_instruction": {"parts": [{"text": messages[0]["content"]}]},
                "contents": history,
            },
            timeout=30,
        )
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]
    except:
     return None

try:
    NAME = json.load(open("user.json", encoding="utf-8"))["name"]
except:
    NAME = "друже"

RULES = " Відповідай українською і коротко. Не допомагай зі шкідливим (безпека). Не вигадуй факти. Пам'ятай розмову."
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
    answer = ask_ai(messages[:1] + messages[1:][-20:])
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
    except OSError:
        return input("Ти: ")  # мікрофона немає
    return ""


ok = 0
bad = 0
while True:
    text = listen()
    if text == "":
        bad += 1
        continue
    ok += 1
    print("Ти сказав:", text)
    open("log_speech.txt", "a", encoding="utf-8").write(str(datetime.now()) + " | " + text + "\n")
    t = text.lower()

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
        print("Біт:", open("log_speech.txt", encoding="utf-8").readlines()[-3:])
    elif "привіт" in t:
        print("Біт: Привіт,", NAME + "!")
    elif "котра година" in t:
        print("Біт: Зараз", datetime.now().strftime("%H:%M"))
    elif "жарт" in t:
        print("Біт: Oct 31 == Dec 25!")
    else:
        print("Я почув:", text)
        print("Біт:", chat(text))
