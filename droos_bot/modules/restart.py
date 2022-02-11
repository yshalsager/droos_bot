""" Bot restart module"""
import pickle
from os import execl
from pathlib import Path
from sys import executable

from telegram import Update, ParseMode
from telegram.ext import CallbackContext, CommandHandler

from droos_bot import dispatcher, PARENT_DIR
from droos_bot.utils.filters import FilterBotAdmin


def restart(update: Update, _: CallbackContext) -> None:
    """restarts the bot."""
    restart_message = update.message.reply_text(
        "`Restarting, please wait...`", parse_mode=ParseMode.MARKDOWN_V2
    )
    chat_info = {"chat": restart_message.chat_id, "message": restart_message.message_id}
    Path(f"{PARENT_DIR}/restart.pickle").write_bytes(pickle.dumps(chat_info))
    execl(executable, executable, "-m", __package__.split(".")[0])


filter_bot_admin = FilterBotAdmin()
dispatcher.add_handler(CommandHandler("restart", restart, filter_bot_admin))
