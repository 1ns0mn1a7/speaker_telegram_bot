from bot.models import Participant, Question, Event
from django.utils.timezone import now


def handle_question(text, user_id, chat_id, context):
    participant, _ = Participant.objects.get_or_create(
        tg_id=user_id,
        defaults={"name": context.bot.get_chat(user_id).username or "Без имени"}
    )
    active_event = Event.objects.filter(start__lte=now(), finish__gte=now(), speaker__isnull=False).first()

    Question.objects.create(author=participant, question=text, event=active_event, tg_chat_id=chat_id)

    try:
        context.bot.send_message(chat_id=chat_id, text="Спасибо! Вопрос получен.")
        if active_event and active_event.speaker and active_event.speaker.tg_id:
            context.bot.send_message(
                chat_id=active_event.speaker.tg_id,
                text=f"Новый вопрос:\n{text}"
            )
    except Exception as error:
        pass
