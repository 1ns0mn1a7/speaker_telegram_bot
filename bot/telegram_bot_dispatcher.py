from bot.handlers.menu import send_main_menu
from bot.handlers.questions import handle_question, handle_speaker_choice, handle_question_for_speaker
from bot.handlers.broadcasts import start_broadcast, handle_broadcast
from bot.handlers.donations import (
    handle_donation_choice,
    handle_fixed_amount,
    request_custom_amount,
    handle_custom_amount,
)
from bot.handlers.events_program import handle_show_program
from bot.handlers.subscriptions import handle_subscription
from bot.handlers.questions_menu import handle_question_flow


def main_message_handler(update, context):
    if not update.message or not update.message.text:
        return

    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    text = update.message.text.strip()
    state = context.bot_data.setdefault("user_states", {})
    user_state = state.get(user_id)

    if isinstance(user_state, dict) and user_state.get("state") == "awaiting_speaker_choice":
        if handle_speaker_choice(text, user_id, chat_id, state, context):
            return

    if isinstance(user_state, dict) and user_state.get("state") == "awaiting_question_text":
        handle_question_for_speaker(text, user_id, chat_id, state, context)
        state[user_id] = None
        return send_main_menu(chat_id, context)

    if user_state == "awaiting_question":
        state[user_id] = None
        handle_question(text, user_id, chat_id, context)
        return send_main_menu(chat_id, context)

    if text == "Задать вопрос":
        handle_question_flow(user_id, chat_id, context, state)
        return

    if text == "Посмотреть программу":
        handle_show_program(chat_id, context)
        return

    if text == "Сделать рассылку" and start_broadcast(user_id, chat_id, context):
        return

    if user_state == "awaiting_broadcast_text":
        handle_broadcast(text, user_id, chat_id, context)
        return

    if text == "Подписаться на рассылку новостей":
        handle_subscription(user_id, chat_id, context)
        return

    if text == "💸 Поддержать":
        handle_donation_choice(update, context)
        return

    if user_state == "choosing_donation" and text.isdigit():
        handle_fixed_amount(text, update, context)
        return

    if user_state == "choosing_donation" and text == "Своя сумма":
        request_custom_amount(update, context)
        return

    if user_state == "awaiting_custom_amount":
        handle_custom_amount(text, update, context)
        return

    if text == "Назад":
        state[user_id] = None
        send_main_menu(chat_id, context)
        return

    state[user_id] = None
    send_main_menu(chat_id, context)
