from telegram import ReplyKeyboardMarkup


def build_main_menu(is_organizer=False):
    buttons = [
        ["Посмотреть программу", "Задать вопрос"],
        ["Подписаться на рассылку новостей"],
        ["💸 Поддержать"]
    ]
    if is_organizer:
        buttons.append(["Сделать рассылку"])
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)


def build_donate_menu():
    buttons = [
        ["100", "200", "500"],
        ["Своя сумма"],
        ["Назад"]
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)
