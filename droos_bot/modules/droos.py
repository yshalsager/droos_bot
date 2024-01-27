"""Droos handler module."""

from functools import partial
from math import ceil

from pandas import DataFrame, Series
from telegram import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from telegram_bot_pagination import InlineKeyboardPaginator

from droos_bot import DATA_COLUMNS, application, sheet
from droos_bot.utils.analytics import add_new_chat_to_db, analysis
from droos_bot.utils.telegram import tg_exceptions_handler

page_size = 5
lecture_components = {
    "book": "📕 الكتاب",
    "main": "📝 المحاور",
    "video": "🎞 فيديو",
    "voice": "🎧 صوتي",
    "text": "📄 تفريغ",
    "summary": "📎 ملخص",
}


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


def get_lecture_message_text(item: Series | DataFrame) -> str:
    if isinstance(item.series, str):
        series_text, lecture = item.series, item.lecture
    else:
        series_text, lecture = item.series.item(), item.lecture.item()
    return f"السلسلة: <b> 🗂{series_text}</b>\n📚 الدرس: <b>{lecture}</b>\n"


def get_data(
    data: Series, data_column_id: str, page: int = 1
) -> tuple[str, InlineKeyboardMarkup]:
    text = "*اختر ما تريد من القائمة:*"
    paginator = InlineKeyboardPaginator(
        ceil(len(data) / page_size),
        current_page=page,
        data_pattern=f"list_{data_column_id}#{{page}}",
    )
    chunk_start: int = (page - 1) * page_size
    data_list = data.iloc[chunk_start : chunk_start + page_size]
    for slug, item in data_list.items():
        paginator.add_before(
            InlineKeyboardButton(
                item.item(), callback_data=f"load_{data_column_id}|{slug}"
            )
        )
    return text, paginator.markup


@tg_exceptions_handler
@add_new_chat_to_db
async def data_command_handler(
    update: Update, _: CallbackContext, data_column_id: str = "series"
) -> None:
    text, reply_markup = get_data(getattr(sheet, data_column_id), data_column_id)
    await update.message.reply_text(text, reply_markup=reply_markup)


@tg_exceptions_handler
async def data_callback_handler(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    query: CallbackQuery = update.callback_query
    await query.answer()
    data_column_id = query.data.split("_")[-1].split("#")[0]
    current_page_callback_value = query.data.split("#")[1]
    current_page = (
        int(current_page_callback_value) if current_page_callback_value else 1
    )
    text, reply_markup = get_data(
        getattr(sheet, data_column_id), data_column_id, page=current_page
    )
    await query.edit_message_text(
        text=text,
        reply_markup=reply_markup,
    )


@tg_exceptions_handler
async def droos_handler(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Send Droos list."""
    query: CallbackQuery = update.callback_query
    await query.answer()
    # get series query
    query_data, slug = query.data.split("|")
    data_column_id = query_data.split("_")[-1]
    if "#" in query.data:
        page_idx = int(query.data.split("#")[1])
        slug = slug.split("#")[0]
    else:
        page_idx = 1
    data: DataFrame = sheet.df[getattr(sheet.df, f"{data_column_id}_slug") == slug]
    if data.empty:
        await query.edit_message_text(
            text="حدث خطأ في جلب البيانات المطلوبة",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "رجوع", callback_data=f"list_{data_column_id}#"
                        )
                    ]
                ]
            ),
        )
        return
    if data_column_id != "series":
        # Handle author/category
        series_data: Series = data.groupby("series_slug")["series"].unique()
        text, reply_markup = get_data(series_data, "series", page=page_idx)
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
        )
        return
    # Handle series
    item: Series = data.iloc[page_idx - 1, :]
    paginator = InlineKeyboardPaginator(
        len(data),
        current_page=page_idx,
        data_pattern=f"load_{data_column_id}|{slug}#{{page}}",
    )
    buttons = []
    for component, name in lecture_components.items():
        if getattr(item, component):
            buttons.append(
                InlineKeyboardButton(name, callback_data=f"getd|{component}|{item.id}")
            )
    paginator.add_before(*buttons)
    paginator.add_after(
        InlineKeyboardButton("رجوع", callback_data=f"list_{data_column_id}#")
    )
    await query.edit_message_text(
        text=get_lecture_message_text(item),
        reply_markup=paginator.markup,
        parse_mode=ParseMode.HTML,
    )


@tg_exceptions_handler
@analysis
async def get_lecture_callback_handler(
    update: Update, _: CallbackContext
) -> Series | None:
    query = update.callback_query
    await query.answer()
    __, data, lecture_id = query.data.split("|")
    lecture_info = sheet.df[sheet.df.id == lecture_id]
    if lecture_info.empty or getattr(lecture_info, data).empty:
        return None
    message_link = getattr(lecture_info, data).item()
    from_chat_id, message_id = await parse_telegram_link(message_link)
    await application.bot.copy_message(
        chat_id=query.message.chat_id,
        from_chat_id=from_chat_id,
        message_id=message_id,
    )
    return lecture_info


# series
for _data_column_id, _data_column_name in DATA_COLUMNS.items():
    application.add_handler(
        MessageHandler(
            filters.Regex(_data_column_name),
            partial(data_command_handler, data_column_id=_data_column_id),
        )
    )
    application.add_handler(
        CallbackQueryHandler(data_callback_handler, pattern=r"^list_[\w]+#")
    )
    # lectures
    application.add_handler(
        CallbackQueryHandler(droos_handler, pattern=r"^load_[\w]+\|")
    )
    application.add_handler(CallbackQueryHandler(droos_handler, pattern=r"^[\w_]+#"))
application.add_handler(
    CallbackQueryHandler(get_lecture_callback_handler, pattern=r"^getd\|")
)
