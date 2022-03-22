from telegram import Update
from telegram.ext import CallbackContext, CommandHandler

from droos_bot import dispatcher
from droos_bot.utils.analytics import add_new_chat_to_db
from droos_bot.utils.keyboards import main_keyboard


@add_new_chat_to_db
def start_handler(update: Update, _: CallbackContext) -> None:
    assert update.effective_user is not None
    welcome_text = (
        f" مرحبا بك يا `{update.effective_user.full_name}`"
        f"\n بإمكانك استخدام البوت من خلال الضغط على الأزرار الظاهرة بالأسفل"
    )
    update.message.reply_text(welcome_text, reply_markup=main_keyboard)


dispatcher.add_handler(CommandHandler("start", start_handler))
dispatcher.add_handler(CommandHandler("help", start_handler))
