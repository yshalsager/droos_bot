"""Admin files handler module."""
from typing import cast

from telegram import Audio, Document, Update, Video, Voice
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from droos_bot import application
from droos_bot.utils.filters import FilterBotAdmin

START_RECEIVING = 1


async def start_receiving(_: Update, __: CallbackContext) -> int:
    return START_RECEIVING


async def stop_receiving(_: Update, __: CallbackContext) -> int:
    return cast(int, ConversationHandler.END)


async def files_receiver(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Send explanation on how to use the bot."""
    assert update.effective_message is not None
    if not isinstance(
        update.effective_message.effective_attachment,
        Document | Audio | Video | Voice | list,
    ):
        message = f"Ͱ`{update.effective_message.text_html_urled}`"
    else:
        file_id = (
            update.effective_message.effective_attachment[-1].file_id
            if isinstance(update.effective_message.effective_attachment, list)
            else update.effective_message.effective_attachment.file_id
        )
        message = f"`{file_id}`Ͱ"
        if update.effective_message.caption_html_urled:
            message += f"`{update.effective_message.caption_html_urled}`"
    await update.effective_message.reply_text(
        message,
    )


filter_bot_admin = FilterBotAdmin()

admin_conversation_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^/receive$"), start_receiving)],
    states={
        START_RECEIVING: [
            MessageHandler(
                ~filters.COMMAND & filter_bot_admin & filters.ChatType.PRIVATE,
                files_receiver,
            )
        ],
    },
    fallbacks=[
        CommandHandler("done", stop_receiving),
    ],
)
application.add_handler(admin_conversation_handler)
