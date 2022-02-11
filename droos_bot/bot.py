"""
Telegram Bot
"""
import pickle
from pathlib import Path

from telegram import ParseMode

from droos_bot import updater, PARENT_DIR
from droos_bot.modules import ALL_MODULES
from droos_bot.utils.modules_loader import load_modules


def main() -> None:
    """Run bot."""
    # Load all modules in modules list
    load_modules(ALL_MODULES, __package__)
    # Start the Bot
    updater.start_polling()
    # Restart handler
    if Path(f"{PARENT_DIR}/restart.pickle").exists():
        restart_message = pickle.loads(
            Path(f"{PARENT_DIR}/restart.pickle").read_bytes()
        )
        updater.bot.edit_message_text(
            "`Restarted Successfully!`",
            restart_message["chat"],
            restart_message["message"],
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        Path("restart.pickle").unlink()
    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
