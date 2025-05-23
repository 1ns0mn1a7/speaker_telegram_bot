from bot.models import Event
from bot.event_utils import update_event_activity
from django.utils.timezone import now


def format_event_info(event, highlight=False):
    date = event.start.strftime("%d.%m.%Y")
    time_range = f"{event.start.strftime('%H:%M')}–{event.finish.strftime('%H:%M')}"
    place = event.place.name if event.place else "Будет определено позже"
    speaker_queryset = event.speaker.all()
    speaker_names = ", ".join(speaker.name for speaker in speaker_queryset)
    speakers = speaker_names or "Будет определено позже"

    return (
        f"Мероприятие: {event.name}\n"
        f"Дата: {date}\n"
        f"Время проведения: {time_range}\n"
        f"Место: {place}\n"
        f"Спикер(ы): {speakers}"
    )


def handle_show_program(chat_id, context):
    update_event_activity()

    events = Event.objects.filter(finish__gte=now()).order_by("start")
    if not events.exists():
        context.bot.send_message(
            chat_id=chat_id,
            text="Пока нет запланированных мероприятий."
        )
        return

    active_events = [event for event in events if event.active]
    upcoming_events = [event for event in events if not event.active]

    if active_events:
        context.bot.send_message(
            chat_id=chat_id,
            text="🕒 <b>Сейчас идёт:</b>",
            parse_mode="HTML"
        )
        for event in active_events:
            message = format_event_info(event)
            context.bot.send_message(chat_id=chat_id, text=message)

    if upcoming_events:
        context.bot.send_message(
            chat_id=chat_id,
            text="📅 <b>Ожидается:</b>",
            parse_mode="HTML"
        )
        for event in upcoming_events:
            message = format_event_info(event)
            context.bot.send_message(chat_id=chat_id, text=message)
