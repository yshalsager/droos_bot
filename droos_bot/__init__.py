"""Bot initialization."""

import json
import logging.config
from functools import partial
from pathlib import Path

from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, Defaults, PicklePersistence

from droos_bot.gsheet.spreadsheet import Spreadsheet
from droos_bot.utils.telegram import handle_restart

# paths
WORK_DIR = Path(__package__)
PARENT_DIR = WORK_DIR.parent

# bot config
CONFIG = json.loads((PARENT_DIR / "config.json").read_text(encoding="utf-8"))
BOT_TOKEN = CONFIG["tg_bot_token"]
TG_BOT_ADMINS = CONFIG["tg_bot_admins"]
DATA_COLUMNS: dict[str, str] = CONFIG["data_columns"]

# Logging
log_file_path = PARENT_DIR / "last_run.log"
logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "detailed": {
            "format": "%(asctime)s [%(levelname)s] %(name)s [%(module)s.%(funcName)s:%(lineno)d]: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": "INFO",
            "formatter": "detailed",
            "filename": log_file_path,
            "when": "midnight",
            "interval": 1,
            "backupCount": 7,
        },
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "detailed",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "": {  # root logger
            "handlers": ["file", "console"],
            "level": "INFO",
            "propagate": True,
        },
    },
}
logging.config.dictConfig(logging_config)

# bot
persistence = PicklePersistence(filepath=f"{PARENT_DIR}/bot.pickle")
defaults = Defaults(parse_mode=ParseMode.MARKDOWN_V2, disable_web_page_preview=True)

application = (
    ApplicationBuilder()
    .token(BOT_TOKEN)
    .defaults(defaults)
    .persistence(persistence)
    .post_init(partial(handle_restart, PARENT_DIR))
    .build()
)
sheet = Spreadsheet(
    f"{PARENT_DIR}/service_account.json",
    CONFIG["sheet_id"],
    CONFIG["sheet_name"],
    DATA_COLUMNS,
)

logging.getLogger("httpx").setLevel(logging.WARNING)
