from bot.models import Participant, Message
from django.utils.timezone import now
from bot.handlers.menu import send_main_menu


def start_broadcast(user_id, chat_id, context):
    p = Participant.objects.filter(tg_id=user_id, organizer=True).first()
    if not p:
        context.bot.send_message(chat_id=chat_id, text="Это доступно только организаторам.")
        return False
    context.bot_data["user_states"][user_id] = "awaiting_broadcast_text"
    context.bot.send_message(chat_id=chat_id, text="Введите текст рассылки:")
    return True


def handle_broadcast(text, user_id, chat_id, context):
    context.bot_data["user_states"][user_id] = None
    header = "⚡ Новость от организаторов:"
    recipients = Participant.objects.filter(subscriber=True, tg_id__isnull=False)

    for sub in recipients:
        try:
            context.bot.send_message(chat_id=sub.tg_id, text=f"<b>{header}</b>\n\n{text}", parse_mode="HTML")
        except Exception:
            pass

    msg = Message.objects.create(header=header, message=text, creation_date=now(), send_status=True)
    msg.recipent.set(recipients)
    context.bot.send_message(chat_id=chat_id, text="Рассылка отправлена ✅")
    send_main_menu(chat_id, context)
