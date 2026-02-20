import json
import sys
from collections.abc import Callable
from datetime import timedelta
from functools import wraps
from pathlib import Path
from time import sleep
from typing import Any, TypeVar, cast

from telegram import BotCommand, BotCommandScopeAllPrivateChats, BotCommandScopeChat, Update
from telegram.error import BadRequest, Forbidden, RetryAfter
from telegram.ext import Application, CommandHandler, ConversationHandler

F = TypeVar("F", bound=Callable[..., Any])


def collect_scoped_commands(application: Application) -> tuple[list[BotCommand], list[BotCommand]]:
    metadata: dict[str, tuple[str, str]] = {}
    for module_name in application.bot_data.get("loaded_modules", []):
        module = sys.modules.get(module_name)
        if module is None:
            continue
        for command, description, scope in getattr(module, "BOT_COMMANDS", []):
            metadata.setdefault(command, (description, scope))

    command_names: set[str] = set(metadata)
    handlers_stack: list[Any] = [
        handler for group_handlers in application.handlers.values() for handler in group_handlers
    ]
    while handlers_stack:
        handler = handlers_stack.pop()
        if isinstance(handler, CommandHandler):
            command_names.update(handler.commands)
            continue
        if not isinstance(handler, ConversationHandler):
            continue
        handlers_stack.extend(handler.entry_points)
        handlers_stack.extend(handler.fallbacks)
        for state_handlers in handler.states.values():
            handlers_stack.extend(state_handlers)

    user_commands: list[BotCommand] = []
    admin_only_commands: list[BotCommand] = []
    for command_name in sorted(command_names):
        description, scope = metadata.get(command_name, (command_name, "user"))
        command = BotCommand(command_name, description)
        if scope == "admin":
            admin_only_commands.append(command)
        else:
            user_commands.append(command)
    return user_commands, admin_only_commands


def tg_exceptions_handler[F: Callable[..., Any]](func: F) -> F:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> F:  # type: ignore[return]
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
            sleep(
                error.retry_after.total_seconds()
                if isinstance(error.retry_after, timedelta)
                else error.retry_after
            )
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
    restart_message_path: Path = Path(f"{parent_dir.absolute()}/restart.json")
    if restart_message_path.exists():
        restart_message = json.loads(restart_message_path.read_text())
        await application.bot.edit_message_text(
            "<code>Restarted Successfully!</code>",
            restart_message["chat"],
            restart_message["message"],
        )
        restart_message_path.unlink()


async def setup_scoped_commands(application: Application, admin_ids: list[int]) -> None:
    user_commands, admin_only_commands = collect_scoped_commands(application)
    admin_commands = [*user_commands, *admin_only_commands]
    await application.bot.set_my_commands(
        user_commands,
        scope=BotCommandScopeAllPrivateChats(),
    )
    for admin_id in admin_ids:
        await application.bot.set_my_commands(
            admin_commands,
            scope=BotCommandScopeChat(chat_id=admin_id),
        )
