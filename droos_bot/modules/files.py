"""
Files handler module.
"""

from telegram import Update, ParseMode
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
        parse_mode=ParseMode.MARKDOWN_V2,
    )


filter_bot_admin = FilterBotAdmin()

messages_handler = MessageHandler(
    (Filters.attachment | Filters.photo) & filter_bot_admin,
    files_receiver,
)
dispatcher.add_handler(messages_handler)
