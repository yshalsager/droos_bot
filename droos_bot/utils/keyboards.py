from telegram import ReplyKeyboardMarkup

from droos_bot import DATA_COLUMNS

main_keyboard = ReplyKeyboardMarkup(
    [
        list(reversed([i for i in DATA_COLUMNS.values()])),
        ["إرسال مواد", "التواصل والاقتراحات", "البحث عن سلسلة"],
    ]
)
cancel_search_keyboard = ReplyKeyboardMarkup([["إلغاء البحث"]])
cancel_keyboard = ReplyKeyboardMarkup([["إنهاء"]])
