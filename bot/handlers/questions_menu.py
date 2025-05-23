from telegram import ReplyKeyboardMarkup
from bot.models import Event
from django.utils.timezone import now
from bot.handlers.menu import send_main_menu


def handle_question_flow(user_id, chat_id, context, state):
    active_event = Event.objects.filter(start__lte=now(), finish__gte=now()).first()

    if not active_event:
        context.bot.send_message(
            chat_id=chat_id,
            text="Нет активных мероприятий. Проверьте позже."
        )
        return

    speakers = active_event.speaker.all()
    if not speakers.exists():
        context.bot.send_message(
            chat_id=chat_id,
            text="Нет спикеров. Проверьте позже."
        )
        return

    state[user_id] = {
        "state": "awaiting_speaker_choice",
        "event_id": active_event.id
    }

    speaker_buttons = [[speaker.name] for speaker in speakers]

    context.bot.send_message(
        chat_id=chat_id,
        text="Кому хотите задать вопрос?",
        reply_markup=ReplyKeyboardMarkup(speaker_buttons, resize_keyboard=True)
    )
