import os
from decimal import Decimal
from telegram import LabeledPrice
from bot.models import Donat, Participant
from bot.keyboards import build_donate_menu


def handle_donation_choice(update, context):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    context.bot_data["user_states"][user_id] = "choosing_donation"
    context.bot.send_message(
        chat_id=chat_id,
        text="Выбери сумму пожертвования:",
        reply_markup=build_donate_menu()
    )


def handle_fixed_amount(text, update, context):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    context.bot_data["user_states"][user_id] = None
    amount = int(text) * 100

    context.bot.send_invoice(
        chat_id=chat_id,
        title="Поддержка проекта",
        description=f"Вы жертвуете {text}₽",
        payload="donate",
        provider_token=os.getenv("TELEGRAM_PROVIDER_TOKEN"),
        currency="RUB",
        prices=[LabeledPrice(label="Поддержать", amount=amount)],
        start_parameter="donate"
    )


def request_custom_amount(update, context):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    context.bot_data["user_states"][user_id] = "awaiting_custom_amount"
    context.bot.send_message(
        chat_id=chat_id,
        text="Введите сумму пожертвования (например, 150):"
    )


def handle_custom_amount(text, update, context):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    try:
        amount = int(text)
        if amount < 10:
            context.bot.send_message(
                chat_id=chat_id,
                text="Минимальная сумма — 10₽. Попробуйте ещё раз."
            )
            return

        context.bot_data["user_states"][user_id] = None

        context.bot.send_invoice(
            chat_id=chat_id,
            title="Поддержка проекта",
            description=f"Вы жертвуете {amount}₽",
            payload="donate",
            provider_token=os.getenv("TELEGRAM_PROVIDER_TOKEN"),
            currency="RUB",
            prices=[LabeledPrice(label="Поддержать", amount=amount * 100)],
            start_parameter="donate"
        )
    except ValueError:
        context.bot.send_message(
            chat_id=chat_id,
            text="Введите сумму числом (например, 150)"
        )


def handle_successful_payment(update, context):
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


def precheckout_callback(update, context):
    query = update.pre_checkout_query
    if query.invoice_payload == "donate":
        query.answer(ok=True)
    else:
        query.answer(ok=False, error_message="Ошибка: неправильный payload.")
