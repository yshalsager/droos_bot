from telegram import ReplyKeyboardMarkup

from droos_bot import CONFIG, DATA_COLUMNS


def create_main_keyboard():
    data_values = [
        [value]
        for key, value in DATA_COLUMNS.items()
        if key not in CONFIG.get("hide", [])
    ]
    main_keyboard_buttons = [*data_values]
    buttons_to_disable = CONFIG.get("disable", [])
    for item in ["إرسال مواد", "التواصل والاقتراحات", "البحث عن سلسلة"]:
        if item not in buttons_to_disable:
            main_keyboard_buttons.append([item])
    return main_keyboard_buttons


main_keyboard = ReplyKeyboardMarkup(create_main_keyboard())
cancel_search_keyboard = ReplyKeyboardMarkup([["إلغاء البحث"]])
cancel_keyboard = ReplyKeyboardMarkup([["إنهاء"]])
