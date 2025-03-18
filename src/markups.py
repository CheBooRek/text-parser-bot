import telebot


def make_menu_markup() -> telebot.types.InlineKeyboardMarkup:
    markup = telebot.types.InlineKeyboardMarkup()
    create_pdf = telebot.types.InlineKeyboardButton("PDF файл", callback_data="create_pdf")
    create_txt = telebot.types.InlineKeyboardButton("TXT файл", callback_data="create_txt")
    get_links = telebot.types.InlineKeyboardButton("Список ссылок", callback_data="parse_links")
    markup.add([create_pdf, create_txt, get_links])
    #back = telebot.types.InlineKeyboardButton("Назад", callback_data="back")
    #markup.add(back)
    return markup

