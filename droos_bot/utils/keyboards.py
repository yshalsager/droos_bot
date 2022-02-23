from telegram import ReplyKeyboardMarkup

main_keyboard = ReplyKeyboardMarkup(
    [
        ["البحث عن سلسلة", "السلاسل العلمية"],
        ["التواصل والاقتراحات", "إرسال مواد"],
    ]
)
cancel_search_keyboard = ReplyKeyboardMarkup([["إلغاء البحث"]])
cancel_keyboard = ReplyKeyboardMarkup([["إنهاء"]])
