from bot.models import Participant
from bot.keyboards import build_main_menu


def start(update, context):
    user = update.effective_user
    Participant.objects.get_or_create(tg_id=user.id, defaults={"name": user.username or "Без имени"})
    update.message.reply_text("Привет! Это бот, в котором ты можешь посмотреть список программ и спикеров.")
    send_main_menu(update.effective_chat.id, context)


def send_main_menu(chat_id, context):
    participant = Participant.objects.filter(tg_id=chat_id).first()
    is_organizer = participant.organizer if participant else False
    context.bot.send_message(
        chat_id=chat_id,
        text="Выбери действие с клавиатуры ниже",
        reply_markup=build_main_menu(is_organizer)
    )
