from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler

from droos_bot import dispatcher
from droos_bot.utils.analytics import add_new_chat_to_db


@add_new_chat_to_db
def start_handler(update: Update, _: CallbackContext) -> None:
    welcome_text = (
        f" مرحبا بك يا {update.effective_user.full_name}"
        f"\n بإمكانك استخدام البوت من خلال الضغط على الأزرار الظاهرة بالأسفل"
    )
    reply_keyboard = ReplyKeyboardMarkup(
        [
            ["البحث عن سلسلة", "السلاسل العلمية"],
            ["التواصل والاقتراحات", "إرسال مواد"],
        ]
    )
    update.message.reply_text(welcome_text, reply_markup=reply_keyboard)


dispatcher.add_handler(CommandHandler("start", start_handler))
dispatcher.add_handler(CommandHandler("help", start_handler))
