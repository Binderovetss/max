import eventlet
eventlet.monkey_patch()

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
import requests
import time
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["https://www.nastyl.shop"]}})  # ✅ Разрешаем запросы только с nastyl.shop
socketio = SocketIO(app, cors_allowed_origins="https://www.nastyl.shop")

# 🔹 Telegram Bot Config
TELEGRAM_BOT_TOKEN = os.getenv("7368319072:AAGRGJU9NqchsjSMGHdVSrKGZEXYfyyRiUE")
CHAT_ID = os.getenv("294154587")

@app.route('/send-to-telegram', methods=['POST'])
def send_to_telegram():
    """Принимает данные от клиента и отправляет их в Telegram"""
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

    print(f"📩 Отправляем запрос в Telegram: {payload}")  # ✅ Логируем перед отправкой

    try:
        response = requests.post(telegram_url, json=payload)
        print(f"📩 Ответ от Telegram: {response.status_code}, {response.text}")  # ✅ Логируем ответ
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка при отправке запроса в Telegram: {e}")
        return jsonify({"error": "Ошибка при отправке в Telegram"}), 500

    return jsonify({"status": "✅ Данные отправлены оператору", "user_id": user_id})

@app.route('/callback', methods=['POST'])
def handle_callback():
    """Обрабатывает нажатия кнопок оператором"""
    data = request.json
    print(f"📩 Получен callback от Telegram: {data}")

    if "callback_query" not in data:
        print("❌ Ошибка: В callback-запросе отсутствует 'callback_query'!")
        return jsonify({"error": "callback_query отсутствует"}), 400

    callback_query = data["callback_query"]
    callback_data = callback_query.get("data")

    if not callback_data:
        print("❌ Ошибка: В callback-запросе отсутствует 'data'!")
        return jsonify({"error": "Отсутствует data"}), 400

    try:
        action, user_id = callback_data.split(":")
    except ValueError:
        print("❌ Ошибка: Некорректный формат callback_data!")
        return jsonify({"error": "Неверный формат callback_data"}), 400

    if action == "redirect_sms":
        print(f"✅ Оператор подтвердил редирект для пользователя {user_id}")
        socketio.emit('redirect', {'user_id': user_id, 'url': "https://www.cikava-kava.com.ua/remont-stakanu-bojlera-kavomashyny-delonghi-pokrokovyj-gid/"})

        telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": callback_query["message"]["chat"]["id"],
            "text": f"✅ Пользователь {user_id} будет перенаправлен!"
        }

        response = requests.post(telegram_url, json=payload)
        print(f"📩 Ответ от Telegram: {response.status_code}, {response.text}")

    return jsonify({"message": "✅ Редирект отправлен!"})

if __name__ == "__main__":
    print("🚀 Запуск Gunicorn...")
    socketio.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 5000)), allow_unsafe_werkzeug=True)
