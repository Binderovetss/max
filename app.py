from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

TELEGRAM_BOT_TOKEN = "7368319072:AAGRGJU9NqchsjSMGHdVSrKGZEXYfyyRiUE"
CHAT_ID = "294154587"

@app.route('/')
def home():
    return "🚀 Сервер работает! Используйте /send для отправки сообщений."

@app.route('/send', methods=['POST'])  # Должен быть метод `POST`
def send_to_telegram():
    """Принимает данные и отправляет их в Telegram"""
    data = request.json
    user_input = data.get("user_input", "")

    if not user_input:
        return jsonify({"error": "Введите данные!"}), 400

    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": f"📩 Новый запрос: {user_input}"
    }

    response = requests.post(telegram_url, json=payload)

    if response.status_code == 200:
        return jsonify({"message": "✅ Данные успешно отправлены!"})
    else:
        return jsonify({"error": "❌ Ошибка отправки!"}), 500

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=10000)
