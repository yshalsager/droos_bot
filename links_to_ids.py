"""A script to convert telegram links in a Google sheet to bot own file IDs."""
import json
import logging
import re
from asyncio import sleep
from pathlib import Path

from convopyro import Conversation
from droos_bot.gsheet.spreadsheet import Spreadsheet
from gspread import Cell
from pyrogram import Client, filters
from pyrogram.types import Audio, Document, Photo, Video, Voice

work_dir = Path(__name__).parent
config = json.loads((work_dir / "config.json").read_text(encoding="utf-8"))
telegram_client = Client(
    "telegram_user_account", api_id=config["tg_api_id"], api_hash=config["tg_api_hash"]
)
Conversation(telegram_client)


async def main() -> None:
    """Read Google sheet (using service account with write access).

    - Find all telegram links, using regex from config file
    - For each link, forwards the message as copy to the deployed bot (it must be running)
    - Read bot reply text and replace link cell with {message.media}τ{reply_message.text}
    :return:
    """
    sheet = Spreadsheet(
        f"{work_dir}/service_account_rw.json",
        config["sheet_id"],
        config["sheet_name"],
        config["data_columns"],
    )
    telegram_links: list[Cell] = sheet.worksheet.sheet.findall(
        re.compile(config["links_regex"])
    )
    if not telegram_links:
        return

    await telegram_client.send_message(config["tg_bot_username"], "/receive")

    for link in telegram_links:
        message = await telegram_client.get_messages(
            f"@{link.value.split('/')[-2]}", int(link.value.split("/")[-1])
        )
        if not message.media:
            message_type = "text"
        else:
            message_type = (
                message.media.value
                if hasattr(message, "media") and hasattr(message.media, "value")
                else None
            )
            media: Photo | Audio | Video | Voice | Document = getattr(
                message, message_type, None
            )
            if not message_type or not media or not hasattr(media, "file_id"):
                logging.warning(f"{link}: can't get media!")
                continue
        await telegram_client.copy_message(
            chat_id=config["tg_bot_username"],
            from_chat_id=message.chat.id,
            message_id=message.id,
        )
        reply_message = await telegram_client.listen.Message(
            filters.chat(config["tg_bot_username"]), timeout=10
        )
        await sleep(2)
        sheet.worksheet.sheet.update_cell(
            link.row, link.col, f"{message_type}τ{reply_message.text}"
        )
        logging.info(f"Updated cell {link}")

    await telegram_client.send_message(config["tg_bot_username"], "/done")


if __name__ == "__main__":
    with telegram_client:
        telegram_client.loop.run_until_complete(main())
