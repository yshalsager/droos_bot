"""Bot update module."""

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from droos_bot import application
from droos_bot.modules.restart import restart
from droos_bot.utils.commands import run_command
from droos_bot.utils.filters import FilterBotAdmin


async def update_(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Update the bot then restart."""
    assert update.effective_message is not None
    assert update.effective_chat is not None
    git_output = run_command("git fetch origin master && git reset --hard origin/master")
    if git_output:
        await update.effective_message.reply_text(
            f"```\n{git_output}\n```",
            reply_to_message_id=update.effective_message.message_id,
        )
    await restart(update, _)


application.add_handler(CommandHandler("update", update_, FilterBotAdmin()))
