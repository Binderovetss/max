import gevent.monkey
gevent.monkey.patch_all()  # ✅ Monkey Patch перед всеми импортами!

import os
import requests
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # ✅ Разрешаем CORS для всех запросов
socketio = SocketIO(app, async_mode="gevent", cors_allowed_origins="*")  # ✅ Исправленный WebSocket

# 🔹 Загружаем переменные окружения
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# 🔹 Проверяем, загружены ли данные из Render
if TELEGRAM_BOT_TOKEN is None or CHAT_ID is None:
    print("❌ Ошибка: TELEGRAM_BOT_TOKEN или CHAT_ID не загружены из окружения!")
else:
    CHAT_ID = int(CHAT_ID)  # ✅ Приводим к int
    print(f"🔹 Загружен TELEGRAM_BOT_TOKEN: {TELEGRAM_BOT_TOKEN[:10]}...")
    print(f"🔹 Загружен CHAT_ID (тип {type(CHAT_ID)}): {CHAT_ID}")

@app.route('/send-to-telegram', methods=['POST'])
def send_to_telegram():
    """Принимает данные от клиента и отправляет их в Telegram"""
    try:
        data = request.json
        print(f"📩 Получены данные: {data}")  # ✅ Логируем входные данные

        if TELEGRAM_BOT_TOKEN is None or CHAT_ID is None:
            print("❌ Ошибка: TELEGRAM_BOT_TOKEN или CHAT_ID не загружены!")
            return jsonify({"error": "Ошибка сервера: переменные окружения не загружены"}), 500

        user_info = f"📩 Новый запрос:\n\nИмя: {data.get('name', 'Не указано')}\nТелефон: {data.get('phone', 'Не указано')}\nКомментарий: {data.get('comment', 'Нет')}"
        
        payload = {
            "chat_id": CHAT_ID,
            "text": user_info
        }

        print(f"📩 Отправляем в Telegram: {payload}")  # ✅ Логируем перед отправкой

        response = requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", json=payload)
        
        print(f"📩 Ответ от Telegram: {response.status_code}, {response.text}")  # ✅ Логируем ответ

        if response.status_code != 200:
            return jsonify({"error": "Ошибка при отправке в Telegram", "telegram_response": response.text}), 500

        return jsonify({"status": "✅ Данные отправлены оператору"})

    except Exception as e:
        print(f"❌ Ошибка сервера: {str(e)}")
        return jsonify({"error": f"❌ Ошибка сервера: {str(e)}"}), 500

if __name__ == "__main__":
    print("🚀 Запуск Gunicorn...")
    socketio.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 5000)), allow_unsafe_werkzeug=True)
