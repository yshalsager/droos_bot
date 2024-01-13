"""Bot custom filters."""
from telegram import Message
from telegram.ext.filters import MessageFilter

from droos_bot import TG_BOT_ADMINS


class FilterBotAdmin(MessageFilter):
    def filter(self, message: Message) -> bool:
        return bool(message.from_user and message.from_user.id in TG_BOT_ADMINS)


class FeedbackMessageFilter(MessageFilter):
    def __init__(self, feedback_chat: int, bot_id: str) -> None:
        super().__init__()
        self.feedback_chat = feedback_chat
        self.bot_id = int(bot_id)

    def filter(self, message: Message) -> bool:
        return bool(
            message.reply_to_message
            and message.reply_to_message.chat_id == self.feedback_chat
            and message.reply_to_message.from_user
            and message.reply_to_message.from_user.id == self.bot_id
        )
