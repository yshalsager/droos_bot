from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from droos_bot import application
from droos_bot.utils.analytics import add_new_chat_to_db
from droos_bot.utils.keyboards import main_keyboard


@add_new_chat_to_db
async def start_handler(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    assert update.effective_chat is not None
    welcome_text = (
        f" مرحبا بك يا `{update.effective_chat.full_name or update.effective_chat.title}`"
        f"\n بإمكانك استخدام البوت من خلال الضغط على الأزرار الظاهرة بالأسفل"
    )
    await update.message.reply_text(welcome_text, reply_markup=main_keyboard)


application.add_handler(CommandHandler("start", start_handler))
application.add_handler(CommandHandler("help", start_handler))
