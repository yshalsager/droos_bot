"""Bot initialization."""

import json
import logging
from functools import partial
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from sys import stderr, stdout

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
LOG_FILE = PARENT_DIR / "last_run.log"
LOG_FORMAT = (
    "%(asctime)s [%(levelname)s] %(name)s "
    "[%(module)s.%(funcName)s:%(lineno)d]: %(message)s"
)
FORMATTER: logging.Formatter = logging.Formatter(LOG_FORMAT)
handler = TimedRotatingFileHandler(LOG_FILE, when="d", interval=1, backupCount=3)
logging.basicConfig(filename=str(LOG_FILE), filemode="w", format=LOG_FORMAT)
OUT = logging.StreamHandler(stdout)
ERR = logging.StreamHandler(stderr)
OUT.setFormatter(FORMATTER)
ERR.setFormatter(FORMATTER)
OUT.setLevel(logging.INFO)
ERR.setLevel(logging.WARNING)
LOGGER = logging.getLogger()
LOGGER.addHandler(OUT)
LOGGER.addHandler(ERR)
LOGGER.addHandler(handler)
LOGGER.setLevel(logging.INFO)

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
