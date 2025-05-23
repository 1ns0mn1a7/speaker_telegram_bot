from bot.models import Participant, Question, Event
from telegram import ReplyKeyboardRemove
from django.utils.timezone import now


def get_user_info(context, user_id):
    user_info = context.bot.get_chat(user_id)
    username = user_info.username or user_info.first_name or "Без имени"
    username_display = f"@{user_info.username}" if user_info.username else username
    return username, username_display


def submit_question(text, user_id, chat_id, event, speaker, context):
    username, username_display = get_user_info(context, user_id)

    participant, _ = Participant.objects.get_or_create(
        tg_id=user_id,
        defaults={"name": username}
    )

    Question.objects.create(
        author=participant,
        question=text,
        event=event,
        tg_chat_id=chat_id
    )

    context.bot.send_message(chat_id=chat_id, text="Спасибо! Вопрос получен.")

    if speaker and speaker.tg_id:
        try:
            context.bot.send_message(
                chat_id=speaker.tg_id,
                text=f"Вопрос от {username_display}:\n\n{text}"
            )
        except Exception:
            pass

    organizers = Participant.objects.filter(organizer=True, tg_id__isnull=False)
    for org in organizers:
        try:
            context.bot.send_message(
                chat_id=org.tg_id,
                text=f"Вопрос для {speaker.name if speaker else 'спикера'}\nот {username_display}:\n\n{text}"
            )
        except Exception:
            pass


def handle_question(text, user_id, chat_id, context):
    active_event = Event.objects.filter(
        start__lte=now(),
        finish__gte=now(),
        speaker__isnull=False
    ).first()
    speaker = active_event.speaker if active_event else None
    submit_question(text, user_id, chat_id, active_event, speaker, context)


def handle_speaker_choice(text, user_id, chat_id, state, context):
    if user_id not in state or "event_id" not in state[user_id]:
        context.bot.send_message(
            chat_id=chat_id,
            text="Что-то пошло не так. Попробуйте сначала."
        )
        return False

    event_id = state[user_id]["event_id"]
    active_event = Event.objects.filter(id=event_id).first()
    speaker = active_event.speaker.filter(name=text).first() if active_event else None
    if not speaker:
        context.bot.send_message(
            chat_id=chat_id,
            text="Спикер не определен. Попробуйте снова."
        )
        return False

    state[user_id] = {
        "state": "awaiting_question_text",
        "event_id": active_event.id,
        "speaker_id": speaker.id
    }

    context.bot.send_message(
        chat_id=chat_id,
        text=f"Введите ваш вопрос для спикера {speaker.name}:",
        reply_markup=ReplyKeyboardRemove()
    )
    return True


def handle_question_for_speaker(text, user_id, chat_id, state, context):
    if user_id not in state or "event_id" not in state[user_id] or "speaker_id" not in state[user_id]:
        context.bot.send_message(
            chat_id=chat_id,
            text="Что-то пошло не так. Попробуйте сначала."
        )
        return

    event_id = state[user_id]["event_id"]
    speaker_id = state[user_id]["speaker_id"]

    event = Event.objects.filter(id=event_id).first()
    speaker = Participant.objects.filter(id=speaker_id).first()

    submit_question(text, user_id, chat_id, event, speaker, context)
