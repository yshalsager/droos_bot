"""Telegram Bot."""
from droos_bot import application
from droos_bot.modules import ALL_MODULES
from droos_bot.utils.modules_loader import load_modules


def main() -> None:
    """Run bot."""
    # Load all modules in modules list
    load_modules(ALL_MODULES, __package__)
    # Start the Bot
    application.run_polling()


if __name__ == "__main__":
    main()
