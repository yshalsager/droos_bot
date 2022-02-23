"""
Bot custom filters
"""
from telegram import Message
from telegram.ext import MessageFilter

from droos_bot import TG_BOT_ADMINS


class FilterBotAdmin(MessageFilter):
    def filter(self, message: Message):
        return message.from_user.id in TG_BOT_ADMINS
