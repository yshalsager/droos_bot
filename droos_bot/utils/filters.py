"""
Bot custom filters
"""
from telegram import Message
from telegram.ext import MessageFilter

from droos_bot import TG_BOT_ADMINS


class FilterBotAdmin(MessageFilter):
    def filter(self, message: Message):
        return message.from_user.id in TG_BOT_ADMINS


class SearchTextFilter(MessageFilter):
    def __init__(self, search_reply_text):
        self.search_reply_text = search_reply_text

    def filter(self, message: Message):
        return (
            bool(message.reply_to_message)
            and message.reply_to_message.text == self.search_reply_text
        )
