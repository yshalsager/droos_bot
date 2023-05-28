"""Bot update module."""

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from droos_bot import PARENT_DIR, application
from droos_bot.modules.restart import restart
from droos_bot.utils.commands import run_command
from droos_bot.utils.filters import FilterBotAdmin


async def update_(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Update the bot then restart."""
    assert update.effective_message is not None
    assert update.effective_chat is not None
    git_output = run_command(
        "git fetch origin master && git reset --hard origin/master"
    )
    if git_output:
        await update.effective_message.reply_text(
            f"```\n{git_output}\n```",
            reply_to_message_id=update.effective_message.message_id,
        )
    # Update the sheet
    sheet_update_output = run_command(f"python3 {PARENT_DIR}/links_to_ids.py")
    sheet_update_clean_output = "\n".join(
        list(filter(lambda x: "pyrogram" not in x, sheet_update_output.splitlines()))
    )
    if not sheet_update_clean_output:
        sheet_update_clean_output = "Nothing to update"
    await update.effective_message.reply_text(
        f"```\n{sheet_update_clean_output}\n```",
        reply_to_message_id=update.effective_message.message_id,
    )
    await restart(update, _)


filter_bot_admin = FilterBotAdmin()
application.add_handler(CommandHandler("update", update_, filter_bot_admin))
