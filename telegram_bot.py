import os
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext


def build_main_menu():
    """Формирует главное меню клавиатуры"""
    buttons = [
        ["Посмотреть программу", "Задать вопрос"]
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)


def send_main_menu(chat_id: int, context: CallbackContext):
    """Отправка главного меню"""
    context.bot.send_message(
        chat_id=chat_id,
        text="Выбери действие с клавиатуры ниже",
        reply_markup=build_main_menu()
    )


def start(update: Update, context: CallbackContext):
    """Команда /start — приветствие + меню"""
    welcome_text = "Привет! Это бот, в котором ты можешь посмотреть список программ и спикеров, а также задать вопросы!"

    chat_id = update.effective_chat.id
    context.bot.send_message(
        chat_id=chat_id,
        text=welcome_text
    )
    send_main_menu(chat_id, context)


def handle_message(update: Update, context: CallbackContext):
    """Обрабатывает текстовые сообщения от пользователя."""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    text = update.message.text.strip()

    user_states = context.bot_data.setdefault("user_states", {})

    if user_states.get(user_id) == "awaiting_question":
        user_states[user_id] = None

        context.bot.send_message(
            chat_id=chat_id,
            text="Спасибо! Вопрос получен."
        )

        admin_chat_id = os.getenv("ADMIN_CHAT_ID")
        if admin_chat_id:
            context.bot.send_message(
                chat_id=admin_chat_id,
                text=f"Новый вопрос от @{update.effective_user.username or 'без имени'}:\n{text}"
            )
        return send_main_menu(chat_id, context)

    if text == "Посмотреть программу":
        context.bot.send_message(chat_id=chat_id, text="Программа пока не загружена.")
        return

    if text == "Задать вопрос":
        user_states[user_id] = "awaiting_question"
        context.bot.send_message(chat_id=chat_id, text="Напиши свой вопрос в следующем сообщении.")
        return

    context.bot.send_message(
        chat_id=chat_id,
        text="Я пока не понимаю это сообщение. Используй меню ниже.",
        reply_markup=build_main_menu()
    )


def main():
    load_dotenv()
    telegram_bot_token = os.getenv("TELEGRAM_TOKEN")

    updater = Updater(telegram_bot_token, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
