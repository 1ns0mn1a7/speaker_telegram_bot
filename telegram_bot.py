import os
import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "telegramm_bot.settings")
django.setup()


from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, LabeledPrice
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, PreCheckoutQueryHandler
from bot.models import Participant, Donat, Question, Event, Message
from django.utils.timezone import now
from decimal import Decimal
from telegram_tools.event_utils import update_event_activity


def build_main_menu(is_organizer=False):
    """Формирует главное меню клавиатуры"""
    buttons = [
        ["Посмотреть программу", "Задать вопрос"],
        ["Подписаться на рассылку новостей"],
        ["💸 Поддержать"]
    ]
    if is_organizer:
        buttons.append(["Сделать рассылку"])
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)


def build_donate_menu():
    """Формирует меню для доната"""
    buttons = [
        ["100", "200", "500"],
        ["Своя сумма"],
        ["Назад"]
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)


def send_main_menu(chat_id: int, context: CallbackContext):
    """Отправка главного меню"""
    participant = Participant.objects.filter(tg_id=chat_id).first()
    is_organizer = participant.organizer if participant else False

    context.bot.send_message(
        chat_id=chat_id,
        text="Выбери действие с клавиатуры ниже",
        reply_markup=build_main_menu(is_organizer=is_organizer)
    )


def start(update: Update, context: CallbackContext):
    """Команда /start — приветствие + меню"""
    welcome_text = "Привет! Это бот, в котором ты можешь посмотреть список программ и спикеров, а также задать вопросы!"

    tg_id = update.effective_user.id
    username = update.effective_user.username or "Без имени"
    Participant.objects.get_or_create(tg_id=tg_id, defaults={"name": username})

    chat_id = update.effective_chat.id
    context.bot.send_message(
        chat_id=chat_id,
        text=welcome_text
    )
    send_main_menu(chat_id, context)


def handle_message(update: Update, context: CallbackContext):
    """Обрабатывает текстовые сообщения от пользователя."""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    text = update.message.text.strip()

    user_states = context.bot_data.setdefault("user_states", {})

    if user_states.get(user_id) == "awaiting_question":
        user_states[user_id] = None

        username = update.effective_user.username or "Без имени"
        participant, _ = Participant.objects.get_or_create(
            tg_id=chat_id,
            defaults={"name": username}
        )

        active_event = Event.objects.filter(
            start__lte=now(),
            finish__gte=now(),
            speaker__isnull=False
        ).first()

        Question.objects.create(
            author=participant,
            question=text,
            event=active_event,
            tg_chat_id=chat_id
        )

        context.bot.send_message(
            chat_id=chat_id,
            text="Спасибо! Вопрос получен."
        )

        if active_event and active_event.speaker and active_event.speaker.tg_id:
            context.bot.send_message(
                chat_id=active_event.speaker.tg_id,
                text=f"Вам пришёл вопрос от участника @{username}:\n{text}"
            )

        organizers = Participant.objects.filter(organizer=True, tg_id__isnull=False)

        for org in organizers:
            context.bot.send_message(
                chat_id=org.tg_id,
                text=f"Новый вопрос от @{username}:\n{text}"
            )
        return send_main_menu(chat_id, context)

    if text == "Посмотреть программу":
        update_event_activity()
        events = Event.objects.filter(finish__gte=now()).order_by("start")

        if not events.exists():
            context.bot.send_message(chat_id=chat_id, text="Пока нет запланированных мероприятий.")
            return

        messages = []
        for event in events:
            title = event.name
            date = event.start.strftime("%d.%m.%Y")
            time_range = f"{event.start.strftime('%H:%M')}–{event.finish.strftime('%H:%M')}"
            place = event.place.name if event.place else "Будет определено позже"
            speaker = event.speaker.name if event.speaker else "Будет определено позже"

            message = (
                f"Мероприятие: {title}\n"
                f"Дата: {date}\n"
                f"Время проведения: {time_range}\n"
                f"Место: {place}\n"
                f"Спикер: {speaker}"
            )

            if event.active:
                message = "Сейчас идёт:\n\n" + message

            messages.append(message)

        for message in messages:
            context.bot.send_message(chat_id=chat_id, text=message)
        return

    if text == "Задать вопрос":
        user_states[user_id] = "awaiting_question"
        context.bot.send_message(chat_id=chat_id, text="Напиши свой вопрос в следующем сообщении.")
        return

    if text == "Подписаться на рассылку новостей":
        chat_id = update.effective_chat.id
        username = update.effective_user.username or "Без имени"

        participant, created = Participant.objects.get_or_create(
            tg_id=chat_id,
            defaults={"name": username}
        )

        if not participant.subscriber:
            participant.subscriber = True
            participant.save()
            context.bot.send_message(chat_id=chat_id, text="Вы подписались на новости спикеров!")
        else:
            context.bot.send_message(chat_id=chat_id, text="Вы уже подписаны.")
        return

    if text == "💸 Поддержать":
        user_states[user_id] = "choosing_donation"
        context.bot.send_message(
            chat_id=chat_id,
            text="Выбери сумму пожертвования:",
            reply_markup=build_donate_menu()
        )
        return

    if user_states.get(user_id) == "choosing_donation" and text.isdigit():
        user_states[user_id] = None
        amount = int(text) * 100

        context.bot.send_invoice(
            chat_id=chat_id,
            title="Поддержка проекта",
            description=f"Вы пожертвовали {text}₽",
            payload="donate_payload_001",
            provider_token=os.getenv("TELEGRAM_PROVIDER_TOKEN"),
            currency="RUB",
            prices=[LabeledPrice(label="Поддержать проект", amount=amount)],
            start_parameter="test-start"
        )
        return

    if user_states.get(user_id) == "choosing_donation" and text == "Своя сумма":
        user_states[user_id] = "awaiting_custom_amount"
        context.bot.send_message(chat_id=chat_id, text="Введите сумму в рублях (например, 150):")
        return

    if user_states.get(user_id) == "awaiting_custom_amount":
        try:
            amount = int(text)
            if amount < 10:
                context.bot.send_message(chat_id=chat_id, text="Минимальная сумма — 10₽. Попробуйте ещё раз.")
                return
            user_states[user_id] = None

            context.bot.send_invoice(
                chat_id=chat_id,
                title="Поддержка проекта",
                description=f"Вы пожертвуете {amount}₽",
                payload="donate_payload_001",
                provider_token=os.getenv("TELEGRAM_PROVIDER_TOKEN"),
                currency="RUB",
                prices=[LabeledPrice(label="Поддержать проект", amount=amount * 100)],
                start_parameter="test-start"
            )
        except ValueError:
            context.bot.send_message(chat_id=chat_id, text="Введите сумму числом (например, 150)")
        return

    if text == "Сделать рассылку":
        participant = Participant.objects.filter(tg_id=user_id).first()
        if participant and participant.organizer:
            user_states[user_id] = "awaiting_broadcast_text"
            context.bot.send_message(chat_id=chat_id, text="Введите текст рассылки для подписчиков:")
        else:
            context.bot.send_message(chat_id=chat_id, text="Эта функция доступна только организаторам.")
        return

    if user_states.get(user_id) == "awaiting_broadcast_text":
        user_states[user_id] = None

        header = "⚡ Новость от организаторов:"
        message_text = text

        recipients = Participant.objects.filter(subscriber=True, tg_id__isnull=False)

        for sub in recipients:
            try:
                context.bot.send_message(
                    chat_id=sub.tg_id,
                    text=f"<b>{header}</b>\n\n{message_text}",
                    parse_mode="HTML"
                )
            except Exception as error:
                pass

        message = Message.objects.create(
            header=header,
            message=message_text,
            creation_date=now(),
            send_status=True
        )
        message.recipent.set(recipients)

        context.bot.send_message(chat_id=chat_id, text="Рассылка отправлена")
        send_main_menu(chat_id, context)
        return

    if text == "Назад":
        user_states[user_id] = None
        send_main_menu(chat_id, context)
        return

    context.bot.send_message(
        chat_id=chat_id,
        text="Я пока не понимаю это сообщение. Используй меню ниже.",
        reply_markup=build_main_menu()
    )


def precheckout_callback(update: Update, context: CallbackContext):
    query = update.pre_checkout_query
    if query.invoice_payload != "donate_payload_001":
        query.answer(ok=False, error_message="Ошибка при обработке платежа.")
    else:
        query.answer(ok=True)


def successful_payment_callback(update: Update, context: CallbackContext):
    tg_id = update.effective_user.id
    username = update.effective_user.username or "Без имени"

    amount_rub = update.message.successful_payment.total_amount / 100

    participant, _ = Participant.objects.get_or_create(
        tg_id=tg_id,
        defaults={"name": username}
    )

    Donat.objects.create(
        donater=participant,
        size=Decimal(str(amount_rub))
    )

    update.message.reply_text("Спасибо за поддержку!")


def main():
    load_dotenv()
    telegram_bot_token = os.getenv("TELEGRAM_TOKEN")

    updater = Updater(telegram_bot_token, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dp.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    dp.add_handler(MessageHandler(Filters.successful_payment, successful_payment_callback))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
