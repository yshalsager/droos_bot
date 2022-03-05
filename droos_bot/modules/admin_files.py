"""
Admin files handler module.
"""

from telegram import Audio, Document, Update, Video, Voice
from telegram.ext import CallbackContext, Filters, MessageHandler

from droos_bot import dispatcher
from droos_bot.utils.filters import FilterBotAdmin


def files_receiver(update: Update, _: CallbackContext) -> None:
    """Sends explanation on how to use the bot."""
    assert update.effective_message is not None
    if not isinstance(
        update.effective_message.effective_attachment,
        (Document, Audio, Video, Voice, list),
    ):
        return None
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

# This conflicts with files_conversation_handler when sender is a bot admin, but it's not a big deal
messages_handler = MessageHandler(
    Filters.attachment & filter_bot_admin & Filters.chat_type.private,
    files_receiver,
)
dispatcher.add_handler(messages_handler)
