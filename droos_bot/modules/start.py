"""
Start handler module.
"""
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler

from droos_bot import dispatcher


def start(update: Update, _: CallbackContext) -> None:
    """Sends explanation on how to use the bot."""
    update.message.reply_text("Hi!")


dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("help", start))
