from functools import wraps
from typing import Any, Callable, TypeVar, cast

from telegram import Update
from telegram.ext import CallbackContext

from droos_bot.db.curd import (
    add_chat_to_db,
    increment_lecture_requests,
    increment_series_requests,
    increment_usage,
)
from droos_bot.utils.telegram import get_chat_type

F = TypeVar("F", bound=Callable[..., Any])


def add_new_chat_to_db(func: F) -> F:
    @wraps(func)
    def wrapper(update: Update, context: CallbackContext, *args, **kwargs) -> F:
        assert update.effective_chat is not None
        assert update.effective_chat.id is not None
        assert (
            update.effective_chat.full_name or update.effective_chat.title
        ) is not None
        add_chat_to_db(
            update.effective_chat.id,
            update.effective_chat.full_name or update.effective_chat.title,
            get_chat_type(update),
        )
        return cast(F, func(update, context, *args, **kwargs))

    return cast(F, wrapper)


def analysis(func: F) -> F:
    @wraps(func)
    def wrapper(update: Update, context: CallbackContext) -> None:
        lecture_info = func(update, context)
        assert update.effective_message is not None
        increment_usage(update.effective_message.chat_id)
        increment_series_requests(lecture_info)
        increment_lecture_requests(lecture_info)

    return cast(F, wrapper)
