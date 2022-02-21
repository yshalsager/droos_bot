from functools import wraps

from telegram import Update
from telegram.ext import CallbackContext

from droos_bot.db.curd import (
    increment_usage,
    increment_series_requests,
    add_chat_to_db,
    increment_lecture_requests,
)
from droos_bot.utils.telegram import get_chat_type


def add_new_chat_to_db(func):
    @wraps(func)
    def wrapper(update: Update, context: CallbackContext):
        add_chat_to_db(
            update.effective_chat.id,
            update.effective_chat.full_name,
            get_chat_type(update),
        )
        return func(update, context)

    return wrapper


def analysis(func):
    @wraps(func)
    def wrapper(update: Update, context: CallbackContext):
        lecture_info = func(update, context)
        increment_usage(update.effective_message.chat_id)
        increment_series_requests(lecture_info)
        increment_lecture_requests(lecture_info)

    return wrapper
