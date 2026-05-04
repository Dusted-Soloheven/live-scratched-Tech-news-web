from pathlib import Path
import json

import requests
from flask import Flask, jsonify, request, send_from_directory


BASE_DIR = Path(__file__).resolve().parent
NEWS_FILE = BASE_DIR / "scraped_news.json"

app = Flask(__name__, static_folder=str(BASE_DIR), static_url_path="")


def load_news():
    if not NEWS_FILE.exists():
        return []

    with NEWS_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if isinstance(data, list):
        return data
    return []       


@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/api/news")
def api_news():
    news_items = load_news()
    return jsonify(
        {
            "count": len(news_items),
            "items": news_items,
        }
    )


@app.route("/api/health")
def api_health():
    return jsonify({"status": "ok"})


@app.route("/api/spell-check", methods=["POST"])
def api_spell_check():
    payload = request.get_json(silent=True) or {}
    word = str(payload.get("word", "")).strip().lower()

    if not word:
        return jsonify({"error": "A word is required."}), 400

    dictionary_url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"

    try:
        response = requests.get(dictionary_url, timeout=10)
    except requests.RequestException:
        return jsonify({"error": "Unable to reach the dictionary service."}), 502

    if not response.ok:
        return jsonify({"word": word, "correct": False}), 200

    data = response.json()
    meanings = data[0].get("meanings", []) if data else []
    first_meaning = meanings[0] if meanings else {}
    first_definition = first_meaning.get("definitions", [{}])[0]

    return jsonify(
        {
            "word": word,
            "correct": True,
            "definition": first_definition.get("definition", "No definition available"),
            "partOfSpeech": first_meaning.get("partOfSpeech", "word"),
        }
    )


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
