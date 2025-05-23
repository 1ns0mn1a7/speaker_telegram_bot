from bot.models import Participant, Question, Event
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
