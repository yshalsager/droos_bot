import pickle
from functools import wraps
from pathlib import Path
from time import sleep
from typing import Any, Callable, TypeVar, cast

from telegram import Update
from telegram.error import BadRequest, Forbidden, RetryAfter
from telegram.ext import Application

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
        except Forbidden as err:
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


async def handle_restart(parent_dir: Path, application: Application) -> None:
    # Restart handler
    restart_message_path: Path = Path(f"{parent_dir.absolute()}/restart.pickle")
    if restart_message_path.exists():
        restart_message = pickle.loads(restart_message_path.read_bytes())
        await application.bot.edit_message_text(
            "`Restarted Successfully!`",
            restart_message["chat"],
            restart_message["message"],
        )
        restart_message_path.unlink()
