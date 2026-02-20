from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters

from droos_bot import application
from droos_bot.utils.analytics import add_new_chat_to_db
from droos_bot.utils.keyboards import main_keyboard

BOT_COMMANDS = [
    ("start", "بدء استخدام البوت", "user"),
    ("help", "عرض طريقة الاستخدام", "user"),
]


@add_new_chat_to_db
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    assert update.effective_chat is not None
    message = update.effective_message
    assert message is not None
    user_data = context.user_data
    assert user_data is not None
    welcome_text = (
        f" مرحبا بك يا <code>{update.effective_chat.full_name or update.effective_chat.title}</code>"
        f"\n بإمكانك استخدام البوت من خلال الضغط على الأزرار الظاهرة بالأسفل"
    )
    user_data["path"] = []
    await message.reply_text(welcome_text, reply_markup=main_keyboard)


application.add_handler(CommandHandler("start", start_handler, filters.ChatType.PRIVATE))
application.add_handler(CommandHandler("help", start_handler, filters.ChatType.PRIVATE))
application.add_handler(
    MessageHandler(
        filters.ChatType.PRIVATE & filters.Regex("^(القائمة الرئيسية 🏠)$"), start_handler
    )
)
