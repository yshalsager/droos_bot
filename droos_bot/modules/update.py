"""Bot update module"""

from telegram import Update
from telegram.ext import CallbackContext, CommandHandler

from droos_bot import PARENT_DIR, dispatcher
from droos_bot.modules.restart import restart
from droos_bot.utils.commands import run_command
from droos_bot.utils.filters import FilterBotAdmin


def update_(update: Update, _: CallbackContext) -> None:
    """update the bot then restart."""
    assert update.effective_message is not None
    assert update.effective_chat is not None
    git_output = run_command(
        "git fetch origin master && git reset --hard origin/master"
    )
    if git_output:
        update.effective_message.reply_text(
            f"```{git_output}```",
            reply_to_message_id=update.effective_message.message_id,
        )
    # Update the sheet
    sheet_update_output = run_command(f"python3 {PARENT_DIR}/links_to_ids.py")
    sheet_update_clean_output = "\n".join(
        list(filter(lambda x: "pyrogram" not in x, sheet_update_output.splitlines()))
    )
    if not sheet_update_clean_output:
        sheet_update_clean_output = "Nothing to update"
    update.effective_message.reply_text(
        f"```{sheet_update_clean_output}```",
        reply_to_message_id=update.effective_message.message_id,
    )
    restart(update, _)


filter_bot_admin = FilterBotAdmin()
dispatcher.add_handler(CommandHandler("update", update_, filter_bot_admin))
