""" Bot restart module"""
import pickle
from os import execl
from pathlib import Path
from sys import executable

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from droos_bot import PARENT_DIR, application
from droos_bot.utils.filters import FilterBotAdmin


async def restart(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """restarts the bot."""
    restart_message = await update.message.reply_text(
        "`Restarting, please wait...`",
    )
    chat_info = {"chat": restart_message.chat_id, "message": restart_message.message_id}
    Path(f"{PARENT_DIR}/restart.pickle").write_bytes(pickle.dumps(chat_info))
    execl(executable, executable, "-m", __package__.split(".")[0])


filter_bot_admin = FilterBotAdmin()
application.add_handler(CommandHandler("restart", restart, filter_bot_admin))
