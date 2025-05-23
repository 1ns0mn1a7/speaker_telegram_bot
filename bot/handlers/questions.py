from bot.models import Participant, Question, Event
from telegram import ReplyKeyboardRemove
from django.utils.timezone import now


def handle_question(text, user_id, chat_id, context):
    user_info = context.bot.get_chat(user_id)
    username = user_info.username or user_info.first_name or "Без имени"

    participant, _ = Participant.objects.get_or_create(
        tg_id=user_id,
        defaults={"name": username}
    )
    active_event = Event.objects.filter(
        start__lte=now(), finish__gte=now(), speaker__isnull=False
    ).first()

    Question.objects.create(
        author=participant,
        question=text,
        event=active_event,
        tg_chat_id=chat_id
    )

    context.bot.send_message(chat_id=chat_id, text="Спасибо! Вопрос получен.")

    if active_event and active_event.speaker and active_event.speaker.tg_id:
        try:
            context.bot.send_message(
                chat_id=active_event.speaker.tg_id,
                text=f"Вопрос от {username}:\n\n{text}"
            )
        except Exception as error:
            pass

    organizers = Participant.objects.filter(organizer=True, tg_id__isnull=False)

    for org in organizers:
        try:
            context.bot.send_message(
                chat_id=org.tg_id,
                text=f"Вопрос от @{username}:\n\n{text}"
            )
        except Exception as error:
            pass


def handle_speaker_choice(text, user_id, chat_id, state, context):
    event_id = state[user_id]["event_id"]
    active_event = Event.objects.filter(id=event_id).first()
    speaker = active_event.speaker.filter(name=text).first() if active_event else None

    if not speaker:
        context.bot.send_message(chat_id=chat_id, text="Спикер не найден. Попробуйте снова.")
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
    user_state = state[user_id]
    event_id = user_state["event_id"]
    speaker_id = user_state["speaker_id"]

    user_info = context.bot.get_chat(user_id)
    username = user_info.username or user_info.first_name or "Без имени"
    participant, _ = Participant.objects.get_or_create(
        tg_id=user_id,
        defaults={"name": username}
    )

    event = Event.objects.filter(id=event_id).first()
    speaker = Participant.objects.filter(id=speaker_id).first()

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
                text=f"Вопрос от @{username}:\n\n{text}"
            )
        except Exception:
            pass

    organizers = Participant.objects.filter(organizer=True, tg_id__isnull=False)
    for organizer in organizers:
        try:
            context.bot.send_message(
                chat_id=organizer.tg_id,
                text=f"Вопрос для {speaker.name} \nот @{username}:\n\n{text}",
            )
        except Exception:
            pass
