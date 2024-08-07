"""Bot restart module."""

import json
from os import execl
from pathlib import Path
from sys import executable

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, filters

from droos_bot import PARENT_DIR, application
from droos_bot.utils.filters import FilterBotAdmin


async def restart(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Restarts the bot."""
    restart_message = await update.message.reply_text(
        "<code>Restarting, please wait...</code>",
    )
    chat_info = {"chat": restart_message.chat_id, "message": restart_message.message_id}
    Path(f"{PARENT_DIR}/restart.json").write_text(json.dumps(chat_info), encoding="utf-8")
    execl(executable, executable, "-m", __package__.split(".")[0])  # noqa: S606


application.add_handler(
    CommandHandler("restart", restart, filters.ChatType.PRIVATE & FilterBotAdmin())
)
