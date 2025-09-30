# app.py
import os
import datetime
import random
import requests
from flask import Flask, request, jsonify, render_template

app = Flask(__name__, template_folder="templates", static_folder="static")

# Config from environment
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "").strip()
NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "").strip()
OMDB_API_KEY = os.environ.get("OMDB_API_KEY", "").strip()
SPOONACULAR_API_KEY = os.environ.get("SPOONACULAR_API_KEY", "").strip()

JOKES = [
    "Why don't scientists trust atoms? Because they make up everything!",
    "Why was the math book sad? Because it had too many problems?",
    "Parallel lines have so much in common… it’s a shame they’ll never meet."
]

FACTS = [
    "The Eiffel Tower can be 15 cm taller during hot days.",
    "Bananas are berries, but strawberries are not.",
    "Sharks existed before trees."
]

def chatbot_response(user_input: str) -> str:
    if not user_input:
        return "Please type something so I can help."

    text = user_input.lower().strip()

    # Exit
    if text in ["exit", "quit", "bye"]:
        return "Goodbye! 👋 Have a wonderful day!"

    # Greetings
    if any(word in text for word in ["hi", "hello", "hey", "yo"]):
        return random.choice([
            "Hello! 👋 How can I help you today?",
            "Hi there! 😊 What would you like to know?",
            "Hey! I’m here to assist you."
        ])

    # How are you
    if "how are you" in text:
        return "I'm doing well — ready to help! How can I assist you?"

    # Time & Date
    if "time" in text and "date" not in text:
        return f"The current time is {datetime.datetime.now().strftime('%H:%M:%S')}."
    if "date" in text:
        return f"Today's date is {datetime.date.today().strftime('%B %d, %Y')}."

    # Jokes & facts
    if "joke" in text and "funny" not in text:
        return random.choice(JOKES)
    if "fact" in text or "random fact" in text:
        return random.choice(FACTS)

    # ===================== New API Rules =====================

    # 1. News API
    if "news" in text:
        topic = "general"
        for t in ["technology", "sports", "politics", "business", "health", "science"]:
            if t in text:
                topic = t
                break
        if not NEWS_API_KEY:
            return f"News API key not set. Cannot fetch {topic} news."
        try:
            url = "https://newsapi.org/v2/top-headlines"
            params = {"apiKey": NEWS_API_KEY, "category": topic, "country": "us", "pageSize": 3}
            r = requests.get(url, params=params, timeout=6).json()
            articles = r.get("articles", [])
            if not articles:
                return f"No {topic} news found today."
            headlines = "\n".join([f"{i+1}. {a['title']}" for i, a in enumerate(articles)])
            return f"Top {topic} news headlines:\n{headlines}"
        except Exception:
            return "Error fetching news."

    # 2. Dictionary / Word Meaning
    if text.startswith("define ") or text.startswith("meaning of "):
        word = text.replace("define ", "").replace("meaning of ", "").strip()
        if not word:
            return "Please provide a word to define."
        try:
            dict_url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
            r = requests.get(dict_url, timeout=6).json()
            if isinstance(r, list):
                meaning = r[0]["meanings"][0]["definitions"][0]["definition"]
                return f"Definition of '{word}': {meaning}"
            return f"Couldn't find definition for '{word}'."
        except Exception:
            return "Error fetching definition."

    # 3. Currency Exchange
    if text.startswith("convert "):
        try:
            parts = text.split()
            if "to" in parts:
                amt_idx = 1
                amount = float(parts[amt_idx])
                from_currency = parts[amt_idx+1].upper()
                to_currency = parts[amt_idx+3].upper()
                url = f"https://api.exchangerate.host/convert?from={from_currency}&to={to_currency}&amount={amount}"
                r = requests.get(url, timeout=6).json()
                result = r.get("result")
                if result is not None:
                    return f"{amount} {from_currency} = {result:.2f} {to_currency}"
            return "Usage: Convert 100 USD to INR"
        except Exception:
            return "Error fetching currency conversion."

    # 4. Chuck Norris / Fun Jokes
    if "funny joke" in text or "chuck norris" in text:
        try:
            r = requests.get("https://api.chucknorris.io/jokes/random", timeout=6).json()
            return r.get("value", "Couldn't fetch joke right now.")
        except Exception:
            return "Error fetching joke."

    # 5. Quotes API
    if "motivate" in text or "quote" in text:
        try:
            r = requests.get("https://api.quotable.io/random", timeout=6).json()
            content = r.get("content")
            author = r.get("author")
            return f'"{content}" — {author}' if content else "Couldn't fetch a quote."
        except Exception:
            return "Error fetching quote."

    # 6. Movie / TV Info
    if "movie" in text or text.startswith("tell me about "):
        movie_name = text.replace("tell me about", "").replace("movie", "").strip()
        if not movie_name:
            return "Please provide a movie name."
        if not OMDB_API_KEY:
            return "OMDb API key not set. Cannot fetch movie info."
        try:
            url = f"http://www.omdbapi.com/?t={requests.utils.requote_uri(movie_name)}&apikey={OMDB_API_KEY}"
            r = requests.get(url, timeout=6).json()
            if r.get("Response") == "True":
                return (f"{r.get('Title')} ({r.get('Year')})\n"
                        f"Actors: {r.get('Actors')}\n"
                        f"Genre: {r.get('Genre')}\n"
                        f"Plot: {r.get('Plot')}")
            return f"Movie '{movie_name}' not found."
        except Exception:
            return "Error fetching movie info."

    # 7. Recipe API
    if "recipe" in text or "cook" in text or "dish" in text:
        try:
            ingredient = text.replace("recipe", "").replace("with", "").strip() or "chicken"
            if not SPOONACULAR_API_KEY:
                return "Spoonacular API key not set. Cannot fetch recipes."
            url = f"https://api.spoonacular.com/recipes/complexSearch?query={ingredient}&number=3&apiKey={SPOONACULAR_API_KEY}"
            r = requests.get(url, timeout=6).json()
            results = r.get("results", [])
            if not results:
                return f"No recipes found with '{ingredient}'."
            recipes = "\n".join([f"{i+1}. {item['title']}" for i, item in enumerate(results)])
            return f"Here are some recipes with {ingredient}:\n{recipes}"
        except Exception:
            return "Error fetching recipes."

    # 8. Translate API
    if text.startswith("translate "):
        try:
            parts = text.replace("translate ", "").split(" to ")
            if len(parts) == 2:
                word, lang = parts
                r = requests.post("https://libretranslate.com/translate",
                                  data={"q": word, "source": "en", "target": lang.lower()},
                                  timeout=6)
                translated = r.json().get("translatedText")
                return translated if translated else "Could not translate."
            return "Usage: Translate hello to French"
        except Exception:
            return "Error translating text."

    # 9. Fun APIs for Students
    if "cat fact" in text:
        try:
            r = requests.get("https://meowfacts.herokuapp.com/", timeout=6).json()
            return r.get("data", ["No fact found."])[0]
        except Exception:
            return "Error fetching cat fact."
    if "dog picture" in text:
        try:
            r = requests.get("https://dog.ceo/api/breeds/image/random", timeout=6).json()
            return r.get("message", "Couldn't fetch dog image.")
        except Exception:
            return "Error fetching dog image."

    # ===================== Existing rules continue =====================

    # Weather: "weather", "weather in <city>" or "what's the weather in <city>"
    if "weather" in text:
        parts = text.split()
        city = None
        if "in" in parts:
            idx = parts.index("in")
            if idx + 1 < len(parts):
                city = " ".join(parts[idx+1:])
        if not city:
            maybe = text.replace("weather", "").replace("what's", "").replace("whats", "").strip()
            if maybe:
                city = maybe
        if not city:
            city = "London"
        if not OPENWEATHER_API_KEY:
            return f"I can't fetch live weather here (OPENWEATHER_API_KEY not set). Try: 'weather in Delhi'."
        try:
            url = "http://api.openweathermap.org/data/2.5/weather"
            params = {"q": city, "appid": OPENWEATHER_API_KEY, "units": "metric"}
            r = requests.get(url, params=params, timeout=6)
            data = r.json()
            if r.status_code == 200 and "main" in data:
                temp = data["main"]["temp"]
                desc = data["weather"][0]["description"]
                return f"The weather in {city.title()} is {temp}°C with {desc}."
            else:
                return f"Couldn't find weather for '{city}'. Please check the city name."
        except Exception:
            return "Error contacting weather service. Try again later."

    # Technology / study help simple rules
    if "python" in text:
        return ("Python is a versatile programming language used for web development, "
                "data science, automation and more. Try: 'explain python lists'.")
    if "javascript" in text or "js" in text:
        return "JavaScript runs in browsers and servers (Node.js). Great for interactive websites."
    if "internet" in text:
        return "The Internet is a global network of networks that uses TCP/IP to connect devices."

    # Short Q&A like "who made you", "your name"
    if "your name" in text or "who are you" in text:
        return "I'm RuleCraft — an all-purpose rule-based assistant (web edition)."

    if "who made you" in text or "who created you" in text:
        return "I was created by a developer using Python, Flask and a set of rules + APIs."

    # Fallback: attempt Wiki summary
    try:
        topic = text
        for prefix in ["tell me about", "what is", "who is", "explain", "define"]:
            if topic.startswith(prefix):
                topic = topic.replace(prefix, "").strip()
        if topic:
            wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.requote_uri(topic)}"
            r = requests.get(wiki_url, timeout=6)
            if r.status_code == 200:
                data = r.json()
                extract = data.get("extract")
                if extract:
                    return extract if len(extract) <= 800 else extract[:780].rsplit(".", 1)[0] + "..."
            return "Sorry, I don't have info on that in my rules. Try rephrasing or ask something else."
    except Exception:
        return "Sorry, I couldn't find that right now."

    # Final catch-all
    return "I don't understand that yet. Try asking about weather, time, jokes, facts, news, or technology."

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    payload = request.get_json(force=True)
    message = payload.get("message", "")
    reply = chatbot_response(message)
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
