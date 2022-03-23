from functools import wraps
from time import sleep
from typing import Any, Callable, TypeVar, cast

from telegram import Update
from telegram.error import BadRequest, RetryAfter, Unauthorized

F = TypeVar("F", bound=Callable[..., Any])


def tg_exceptions_handler(func: F) -> F:
    @wraps(func)
    def wrapper(*args, **kwargs) -> F:  # type: ignore
        try:
            return cast(F, func(*args, **kwargs))
        except BadRequest as err:
            if "Message is not modified" in err.message:
                pass
            else:
                raise err
        except Unauthorized as err:
            if "bot was blocked by the user" in err.message:
                pass
            else:
                raise err
        except RetryAfter as error:
            sleep(error.retry_after)
            return tg_exceptions_handler(cast(F, func(*args, **kwargs)))

    return cast(F, wrapper)


def get_chat_type(update: Update) -> int:
    chat = update.effective_chat
    assert chat is not None
    return (
        0
        if chat.type == chat.PRIVATE
        else 1
        if chat.type == chat.GROUP
        else 2  # chat.type == chat.CHANNEL
    )
