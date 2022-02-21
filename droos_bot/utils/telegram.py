from functools import wraps
from time import sleep

from telegram import Update
from telegram.error import BadRequest, RetryAfter


def tg_exceptions_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except BadRequest as err:
            if "Message is not modified" in err.message:
                pass
            else:
                raise err
        except RetryAfter as error:
            sleep(error.retry_after)
            return tg_exceptions_handler(func(*args, **kwargs))

    return wrapper


def get_chat_type(update: Update) -> int:
    chat = update.effective_chat
    return (
        0
        if chat.type == chat.PRIVATE
        else 1
        if chat.type == chat.GROUP
        else 2  # chat.type == chat.CHANNEL
    )
