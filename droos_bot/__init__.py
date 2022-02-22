""" Bot initialization """
import json
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from sys import stdout, stderr

from telegram import ParseMode
from telegram.ext import Updater, PicklePersistence, Defaults

from droos_bot.gsheet.spreadsheet import Spreadsheet

# paths
WORK_DIR = Path(__package__)
PARENT_DIR = WORK_DIR.parent

# bot config
CONFIG = json.loads((PARENT_DIR / "config.json").read_text(encoding="utf-8"))
BOT_TOKEN = CONFIG["tg_bot_token"]
TG_BOT_ADMINS = CONFIG["tg_bot_admins"]

# Logging
LOG_FILE = PARENT_DIR / "last_run.log"
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s [%(module)s.%(funcName)s:%(lineno)d]: %(message)s"
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
persistence = PicklePersistence(filename=f"{PARENT_DIR}/bot.pickle")
defaults = Defaults(
    parse_mode=ParseMode.MARKDOWN_V2, run_async=True, disable_web_page_preview=True
)
updater = Updater(
    BOT_TOKEN, persistence=persistence, use_context=True, defaults=defaults
)
dispatcher = updater.dispatcher
sheet = Spreadsheet(
    f"{PARENT_DIR}/service_account.json", CONFIG["sheet_id"], CONFIG["sheet_name"]
)
