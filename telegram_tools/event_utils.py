from django.utils.timezone import now
from bot.models import Event


def update_event_activity():
    """Обновляет флаг активности мероприятий по текущему времени."""
    current_time = now()
    updated = 0

    for event in Event.objects.all():
        is_now = event.start <= current_time <= event.finish
        if event.active != is_now:
            event.active = is_now
            event.save()
            updated += 1

    return updated
