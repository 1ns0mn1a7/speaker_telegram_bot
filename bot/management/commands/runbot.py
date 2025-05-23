from django.core.management.base import BaseCommand
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, PreCheckoutQueryHandler
from dotenv import load_dotenv
import os

from bot.handlers.menu import start
from bot.handlers.donations import handle_successful_payment, precheckout_callback
from bot.telegram_bot_dispatcher import main_message_handler


class Command(BaseCommand):
    help = "Запускает Telegram-бота"

    def handle(self, *args, **options):
        load_dotenv()
        token = os.getenv("TELEGRAM_TOKEN")
        updater = Updater(token, use_context=True)
        dp = updater.dispatcher

        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, main_message_handler))
        dp.add_handler(PreCheckoutQueryHandler(precheckout_callback))
        dp.add_handler(MessageHandler(Filters.successful_payment, handle_successful_payment))

        self.stdout.write(self.style.SUCCESS("Бот запущен"))
        updater.start_polling()
        updater.idle()
