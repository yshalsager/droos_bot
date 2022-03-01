"""
Admin files handler module.
"""

from telegram import Update
from telegram.ext import CallbackContext, MessageHandler, Filters

from droos_bot import dispatcher
from droos_bot.utils.filters import FilterBotAdmin


def files_receiver(update: Update, _: CallbackContext) -> None:
    """Sends explanation on how to use the bot."""
    file_id = (
        update.message.effective_attachment[-1].file_id
        if isinstance(update.message.effective_attachment, list)
        else update.message.effective_attachment.file_id
    )
    message = f"```{file_id}Ͱ"
    if update.effective_message.caption_markdown_v2_urled:
        message += update.effective_message.caption_markdown_v2_urled
    message += "```"
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
