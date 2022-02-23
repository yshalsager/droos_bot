"""
A script to convert telegram links in a Google sheet to bot own file IDs
"""
import json
import re
from asyncio import sleep
from pathlib import Path
from typing import List, Union

from convopyro import Conversation
from gspread import Cell
from pyrogram import Client, filters
from pyrogram.types import Audio, Photo, Video, Voice, Document

from droos_bot.gsheet.spreadsheet import Spreadsheet

work_dir = Path(__name__).parent
config = json.loads((work_dir / "config.json").read_text(encoding="utf-8"))
telegram_client = Client(
    "telegram_user_account", api_id=config["tg_api_id"], api_hash=config["tg_api_hash"]
)
Conversation(telegram_client)


async def main():
    """
    - Read Google sheet (using service account with write access)
    - Find all telegram links, using regex from config file
    - For each link, forwards the message as copy to the deployed bot (it must be running)
    - Read bot reply text and replace link cell with {message.media}τ{reply_message.text}
    :return:
    """
    sheet = Spreadsheet(
        f"{work_dir}/service_account_rw.json", config["sheet_id"], config["sheet_name"]
    )
    telegram_links: List[Cell] = sheet.worksheet.sheet.findall(
        re.compile(config["links_regex"])
    )
    if not telegram_links:
        return

    for link in telegram_links:
        message = await telegram_client.get_messages(
            f"@{link.value.split('/')[-2]}", int(link.value.split("/")[-1])
        )
        if not message.media:
            print(f"{link}: no media")
            continue
        media: Union[Photo, Audio, Video, Voice, Document] = getattr(
            message, str(message.media)
        )
        if not media or not hasattr(media, "file_id"):
            print(f"{link}: can't get media!")
            continue
        await telegram_client.copy_message(
            chat_id=config["tg_bot_username"],
            from_chat_id=message.chat.id,
            message_id=message.message_id,
        )
        reply_message = await telegram_client.listen.Message(
            filters.chat(config["tg_bot_username"]), timeout=10
        )
        await sleep(2)
        sheet.worksheet.sheet.update_cell(
            link.row, link.col, f"{message.media}τ{reply_message.text}"
        )


if __name__ == "__main__":
    with telegram_client:
        telegram_client.loop.run_until_complete(main())
