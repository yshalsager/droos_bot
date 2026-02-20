"""Telegram Bot."""

from droos_bot import application
from droos_bot.modules import ALL_MODULES
from droos_bot.utils.modules_loader import load_modules


def main() -> None:
    """Run bot."""
    # Load all modules in modules list
    application.bot_data["loaded_modules"] = load_modules(ALL_MODULES, __package__ or "droos_bot")
    # Start the Bot
    application.run_polling()


if __name__ == "__main__":
    main()
