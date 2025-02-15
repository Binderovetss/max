import os
import requests
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["https://www.nastyl.shop"]}})
socketio = SocketIO(app, cors_allowed_origins="https://www.nastyl.shop")

# 🔹 Загружаем переменные окружения
TELEGRAM_BOT_TOKEN = os.getenv("7368319072:AAGRGJU9NqchsjSMGHdVSrKGZEXYfyyRiUE")
CHAT_ID = int(os.getenv("CHAT_ID", "0"))  # ✅ Принудительно приводим к int

print(f"🔹 Загружен TELEGRAM_BOT_TOKEN: {TELEGRAM_BOT_TOKEN[:10]}...")
print(f"🔹 Загружен CHAT_ID (тип {type(CHAT_ID)}): {CHAT_ID}")  # ✅ Проверяем, загружается ли CHAT_ID

@app.route('/send-to-telegram', methods=['POST'])
def send_to_telegram():
    data = request.json
    user_id = str(int(time.time()))

    user_info = f"📩 Новый запрос:\n\nИмя: {data.get('name', 'Не указано')}\nТелефон: {data.get('phone', 'Не указано')}\nКомментарий: {data.get('comment', 'Нет')}"

    keyboard = {
        "inline_keyboard": [
            [{"text": "📩 Отправить SMS", "callback_data": f"redirect_sms:{user_id}"}]
        ]
    }

    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": user_info,
        "reply_markup": keyboard
    }

    print(f"📩 Отправляем запрос в Telegram: {payload}")

    try:
        response = requests.post(telegram_url, json=payload)
        print(f"📩 Ответ от Telegram: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка при отправке запроса в Telegram: {e}")
        return jsonify({"error": "Ошибка при отправке в Telegram"}), 500

    return jsonify({"status": "✅ Данные отправлены оператору", "user_id": user_id})
