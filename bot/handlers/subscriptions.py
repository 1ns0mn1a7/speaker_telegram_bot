from bot.models import Participant


def handle_subscription(user_id, chat_id, context):
    participant, _ = Participant.objects.get_or_create(tg_id=user_id)

    if not participant.subscriber:
        participant.subscriber = True
        participant.save()
        context.bot.send_message(chat_id=chat_id, text="Вы подписались на новости!")
    else:
        context.bot.send_message(chat_id=chat_id, text="Вы уже подписаны.")
