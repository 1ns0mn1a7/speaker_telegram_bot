# PythonMeetup

Telegram-бот для Meet Up'ов. 

Позволяет участникам:
* Смотреть программу
* Задавать вопросы спикерам
* Смотреть 
* Подписаться на рассылку новостей
* Делать донаты прямо в Telegram

## Установка
```bash
git clone https://github.com/your-username/speaker_telegram_bot.git
cd speaker_telegram_bot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Переменные окружения
```
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_PROVIDER_TOKEN=your_payment_provider_token
```

## Запуск
```bash
python telegram_bot.py
```

### Что может понадобиться для тестов?

Подключена платформа **ЮMoney** в режиме теста.

Прикладываю парочку тестовых банковских карт для тестирования функции донатов:
1. `5555 5555 5555 4477`
2. `4111 1111 1111 1111`

*PIN / Срок действия указываете любой*.