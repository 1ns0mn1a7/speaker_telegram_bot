from django.core.management.base import BaseCommand
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, PreCheckoutQueryHandler
from dotenv import load_dotenv
import os

from bot.handlers.menu import start, send_main_menu
from bot.handlers.questions import handle_question
from bot.handlers.broadcasts import start_broadcast, handle_broadcast
from bot.handlers.donations import (
    handle_donation_choice,
    handle_fixed_amount,
    request_custom_amount,
    handle_custom_amount,
    handle_successful_payment,
    precheckout_callback
)
from bot.models import Participant
from bot.event_utils import update_event_activity
from bot.models import Event
from django.utils.timezone import now


class Command(BaseCommand):
    help = "Запускает Telegram-бота"

    def handle(self, *args, **options):
        load_dotenv()
        token = os.getenv("TELEGRAM_TOKEN")
        updater = Updater(token, use_context=True)
        dp = updater.dispatcher

        def handle(update, context):
            user_id = update.effective_user.id
            chat_id = update.effective_chat.id
            text = update.message.text.strip()
            state = context.bot_data.setdefault("user_states", {})

            if state.get(user_id) == "awaiting_question":
                state[user_id] = None
                handle_question(text, user_id, chat_id, context)
                return send_main_menu(chat_id, context)

            if text == "Задать вопрос":
                state[user_id] = "awaiting_question"
                context.bot.send_message(
                    chat_id=chat_id,
                    text="Напиши свой вопрос в следующем сообщении:"
                )
                return

            if text == "Сделать рассылку":
                if start_broadcast(user_id, chat_id, context):
                    return

            if state.get(user_id) == "awaiting_broadcast_text":
                handle_broadcast(text, user_id, chat_id, context)
                return

            if text == "Посмотреть программу":
                update_event_activity()
                events = Event.objects.filter(finish__gte=now()).order_by("start")
                if not events.exists():
                    context.bot.send_message(
                        chat_id=chat_id,
                        text="Пока нет запланированных мероприятий."
                    )
                    return

                for event in events:
                    date = event.start.strftime("%d.%m.%Y")
                    time_range = f"{event.start.strftime('%H:%M')}–{event.finish.strftime('%H:%M')}"
                    place = event.place.name if event.place else "Будет определено позже"
                    speaker = event.speaker.name if event.speaker else "Будет определено позже"
                    message = (
                        f"Мероприятие: {event.name}\n"
                        f"Дата: {date}\n"
                        f"Время проведения: {time_range}\n"
                        f"Место: {place}\n"
                        f"Спикер: {speaker}"
                    )
                    if event.active:
                        message = "Сейчас идёт:\n\n" + message
                    context.bot.send_message(chat_id=chat_id, text=message)
                return

            if text == "Подписаться на рассылку новостей":
                participant, _ = Participant.objects.get_or_create(tg_id=user_id)
                if not participant.subscriber:
                    participant.subscriber = True
                    participant.save()
                    context.bot.send_message(chat_id=chat_id, text="Вы подписались на новости!")
                else:
                    context.bot.send_message(chat_id=chat_id, text="Вы уже подписаны.")
                return

            if text == "💸 Поддержать":
                handle_donation_choice(update, context)
                return

            if state.get(user_id) == "choosing_donation" and text.isdigit():
                handle_fixed_amount(text, update, context)
                return

            if state.get(user_id) == "choosing_donation" and text == "Своя сумма":
                request_custom_amount(update, context)
                return

            if state.get(user_id) == "awaiting_custom_amount":
                handle_custom_amount(text, update, context)
                return

            if text == "Назад":
                state[user_id] = None
                send_main_menu(chat_id, context)
                return

            send_main_menu(chat_id, context)

        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle))
        dp.add_handler(PreCheckoutQueryHandler(precheckout_callback))
        dp.add_handler(MessageHandler(Filters.successful_payment, handle_successful_payment))

        self.stdout.write(self.style.SUCCESS("Бот запущен"))
        updater.start_polling()
        updater.idle()
