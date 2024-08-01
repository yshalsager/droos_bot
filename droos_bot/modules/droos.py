"""Droos handler module."""

import re
from typing import Any

from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

from droos_bot import DATA_COLUMNS, LECTURE_COMPONENTS, application, sheet
from droos_bot.modules.start import start_handler
from droos_bot.utils.analytics import add_new_chat_to_db, analysis
from droos_bot.utils.keyboards import create_keyboard
from droos_bot.utils.telegram import tg_exceptions_handler

COMPONENTS_KEYS = {v: k for k, v in LECTURE_COMPONENTS.items()}


async def parse_telegram_link(telegram_link: str) -> tuple[str, str]:
    telegram_chat, message_id = telegram_link.split("/")[-2:]
    if telegram_chat.startswith("-") or telegram_chat.isdigit():
        telegram_chat_id = telegram_chat
    elif application.bot_data.get("chats", {}).get(telegram_chat):
        telegram_chat_id = application.bot_data["chats"][telegram_chat]
    else:
        telegram_chat_id = (await application.bot.get_chat(f"@{telegram_chat}")).id
        if application.bot_data.get("chats"):
            application.bot_data["chats"][telegram_chat] = telegram_chat_id
        else:
            application.bot_data["chats"] = {telegram_chat: telegram_chat_id}
    return telegram_chat_id, message_id


@tg_exceptions_handler
@add_new_chat_to_db
async def handle_navigation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.message.text.lstrip("•").strip()
    user_data = context.user_data
    page = 0
    if query == "🔙 رجوع":
        if user_data.get("path"):
            user_data["path"].pop()
        if not user_data.get("path"):
            return await start_handler(update, context)
    elif any(i in query for i in ("«", "»")):
        # Handle first and last page navigation
        page = 0 if "«" in query else -1
    elif (
        query.startswith("🔶")
        or any(i in query for i in ("←", "→"))
        or (query.isdigit() and not update.message.text.startswith("•"))
    ):
        match = re.search(r"(\d+)", query)
        page = int(match.group(1)) - 1 if match else 0
    else:
        if "path" not in user_data:
            user_data["path"] = []
        # search results
        if " > " in query:
            user_data["path"] = query.split(" > ")
        else:
            user_data["path"].append(query)

    current_level = sheet.navigate_hierarchy(user_data["path"])
    assert current_level is not None

    if "__data" in current_level:
        await update.message.reply_text(
            (
                f"السلسلة: <b> 🗂{user_data['path'][-2]}</b>\n📚 الدرس: <b>{user_data['path'][-1]}</b>\n"
            ),
            reply_markup=create_keyboard(
                [value for key, value in LECTURE_COMPONENTS.items() if current_level.get(key)],
                show_back=True,
                show_pagination=False,
                show_bullet=False,
            ),
        )
    else:
        await update.message.reply_text(
            f"{' > '.join(user_data.get('path', [])) or 'اختر ما تريد'}",
            reply_markup=create_keyboard(
                list(current_level.keys()),
                show_back=bool(user_data.get("path", [])),
                current_page=page,
            ),
        )
    return None


@tg_exceptions_handler
@analysis
async def handle_resource_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> dict[str, Any] | None:
    query = update.message.text.lower()
    current_path = context.user_data.get("path", [])
    current_level = sheet.navigate_hierarchy(current_path)
    if not current_level or not current_level.get("__data"):
        await update.message.reply_text("لم يتم العثور على الدرس المطلوب")
        await start_handler(update, context)
        return None
    from_chat_id, message_id = await parse_telegram_link(current_level[COMPONENTS_KEYS[query]])
    await application.bot.copy_message(
        chat_id=update.message.chat_id,
        from_chat_id=from_chat_id,
        message_id=message_id,
    )
    return current_level


# lecture components
application.add_handler(
    MessageHandler(
        filters.Regex(f"^({'|'.join(i for i in LECTURE_COMPONENTS.values())})$"),
        handle_resource_selection,
    )
)
# data columns
for _data_column_id, _data_column_name in DATA_COLUMNS.items():
    application.add_handler(
        MessageHandler(
            filters.ChatType.PRIVATE & filters.Regex(_data_column_name),
            handle_navigation,
        )
    )
# navigation
application.add_handler(
    MessageHandler(
        filters.ChatType.PRIVATE & ~filters.COMMAND & (filters.Regex(r"[«»←→🔶\d]|🔙 رجوع|•")),
        handle_navigation,
    )
)
