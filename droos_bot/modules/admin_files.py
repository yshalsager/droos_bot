"""
Admin files handler module.
"""

from telegram import Audio, Document, Update, Video, Voice
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    ConversationHandler,
    Filters,
    MessageHandler,
)

from droos_bot import dispatcher
from droos_bot.utils.filters import FilterBotAdmin

START_RECEIVING = 1


def start_receiving(_: Update, __: CallbackContext) -> int:
    return START_RECEIVING


def stop_receiving(_: Update, __: CallbackContext) -> int:
    return ConversationHandler.END


def files_receiver(update: Update, _: CallbackContext) -> None:
    """Sends explanation on how to use the bot."""
    assert update.effective_message is not None
    if not isinstance(
        update.effective_message.effective_attachment,
        (Document, Audio, Video, Voice, list),
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
    update.effective_message.reply_text(
        message,
    )


filter_bot_admin = FilterBotAdmin()

admin_conversation_handler = ConversationHandler(
    entry_points=[MessageHandler(Filters.regex("^/receive$"), start_receiving)],
    states={
        START_RECEIVING: [
            MessageHandler(
                ~Filters.command & filter_bot_admin & Filters.chat_type.private,
                files_receiver,
            )
        ],
    },
    fallbacks=[
        CommandHandler("done", stop_receiving),
    ],
)
dispatcher.add_handler(admin_conversation_handler)
