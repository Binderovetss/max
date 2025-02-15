from flask import Flask, request, jsonify
from flask_socketio import SocketIO
import requests
import time
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # WebSocket для редиректа

# 🔹 Telegram Bot Config
TELEGRAM_BOT_TOKEN = os.getenv("7368319072:AAGRGJU9NqchsjSMGHdVSrKGZEXYfyyRiUE")  # Берём из Render ENV
CHAT_ID = os.getenv("294154587")  # ID чата оператора

# 🔹 Хранилище активных пользователей
active_users = {}

@app.route('/send-to-telegram', methods=['POST'])
def send_to_telegram():
    """Принимает данные от пользователя и отправляет оператору"""
    data = request.json
    user_id = str(int(time.time()))  # Уникальный ID для пользователя

    active_users[user_id] = data  # Запоминаем пользователя

    user_info = f"📩 Новый запрос:\n\nИмя: {data.get('name', 'Не указано')}\nТелефон: {data.get('phone', 'Не указано')}\nКомментарий: {data.get('comment', 'Нет')}"

    # 🔹 Создаём inline-кнопку для оператора
    keyboard = {
        "inline_keyboard": [
            [{"text": "📩 Отправить SMS", "callback_data": f"redirect_sms:{user_id}"}]
        ]
    }

    # 🔹 Отправляем сообщение в Telegram
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": user_info,
        "reply_markup": keyboard
    }
    requests.post(telegram_url, json=payload)

    return jsonify({"status": "✅ Данные отправлены оператору", "user_id": user_id})

@app.route('/callback', methods=['POST'])
def handle_callback():
    """Обрабатывает нажатие кнопки оператором"""
    data = request.json
    if "callback_query" not in data:
        return jsonify({"error": "callback_query отсутствует"}), 400

    callback_query = data["callback_query"]
    callback_data = callback_query.get("data")

    action, user_id = callback_data.split(":")
    
    if action == "redirect_sms":
        if user_id in active_users:
            # 🔹 Отправляем WebSocket-сообщение для редиректа
            socketio.emit('redirect', {'user_id': user_id, 'url': "https://www.cikava-kava.com.ua/remont-stakanu-bojlera-kavomashyny-delonghi-pokrokovyj-gid/"})

            # 🔹 Уведомляем оператора в Telegram
            telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": CHAT_ID,
                "text": f"✅ Пользователь {user_id} будет перенаправлен!"
            }
            requests.post(telegram_url, json=payload)

        return jsonify({"message": "✅ Редирект отправлен!"})

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)