from functools import wraps
from time import sleep

from telegram.error import BadRequest, RetryAfter


def tg_exceptions_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except BadRequest as err:
            if "Message is not modified" in err.message:
                pass
            raise err
        except RetryAfter as error:
            sleep(error.retry_after)
            return tg_exceptions_handler(func(*args, **kwargs))

    return wrapper
