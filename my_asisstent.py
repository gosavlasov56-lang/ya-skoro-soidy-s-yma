import random
from datetime import datetime

KEYWORDS = {
    "greeting": ["привіт", "вітаю", "добрий"],
    "time": ["годин", "котра", "час"],
    "motivation": ["мотивуй", "підтрим", "сил"],
    "help": ["допомога", "вмієш", "можеш"],
}

def clean(text):
    text = text.lower().strip()
    for ch in "?!.,":
        text = text.replace(ch, "")
    return text

def analyze(user_text):
    text = clean(user_text)
    for topic, words in KEYWORDS.items():
        for word in words:
            if word in text:
                return topic
    return "unknown"

def greeting_scenario():
    return random.choice(GREETINGS)

def time_scenario():
    return f"Зараз {datetime.now().strftime('%H:%M')}. Я перевірив двічі."

def motivation_scenario():
    return random.choice(MOTIVATION)

def help_scenario():
    return random.choice(ME)


def respond(topic):
    if topic == "greeting":
        return greeting_scenario()
    elif topic == "time":
        return time_scenario()
    elif topic == "motivation":
        return motivation_scenario()
    elif topic == "help":
        return help_scenario()
    return random.choice(UNKNOWN)


UNKNOWN = [
    "Не розумію, напиши занаво",
    "Не розумію що ти написав",
    "Напиши по іньшому, не розумію ",
]

MOTIVATION = [
    "Я бачю твій прогрес, не зупиняйся зараз далі тільки більше.",
    "Уяви іх облича коли у ти будешь першим.",
    "Согодні ти вже знаешь більше ніж учора, а завтра більше ніж сьогодні.",
]
GREETINGS = [
    "Добрий день",
    "Вітаю тебе",
    "І тобі привіт",
]
ME = [
    "Я можу допомогти тобі у розуміні темі яку ти не зразумів.",
    "Я можу зробити твое домашнне завдання.",
    "Я можу навчити тебе чомусь .",
]
NAME = "Некс"


def get_response(user_text):
    text = user_text.lower().strip()
    if text == "привіт":
        return random.choice(GREETINGS)
    elif text == "хто ти":
        return "Я Некс, твій помічник для навчання."
    elif "можеш" in text:  # треба написату фарзу типу що ти можешь
        return random.choice(ME)
    elif text == "Допоможи мені":
        return "Добре, зараз допомогу ."
    elif text == "Що ти робиш ?":
        return "Я допомагаю тобі у навчані."
    elif "мотивуй" in text: # треба написату фарзу типу замотевуй мене
        return random.choice(MOTIVATION)
    return random.choice(UNKNOWN)


print(f"{NAME}: Вітаю, дорогий користувачу!")
while True:
    user_text = input("Ти: ")
    if clean(user_text) == "бувай":
        print(f"{NAME}: До швидкої зустрічі, дорогий користувачу!")
        break
    topic = analyze(user_text)
    print(f"{NAME}: {respond(topic)}")
