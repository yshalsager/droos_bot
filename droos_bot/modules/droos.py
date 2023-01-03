"""
Droos handler module.
"""
from functools import partial
from typing import Optional, Tuple, Union

from pandas import DataFrame, Series
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.ext import CallbackContext, CallbackQueryHandler, Filters, MessageHandler
from telegram_bot_pagination import InlineKeyboardPaginator

from droos_bot import DATA_COLUMNS, dispatcher, sheet
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


def get_lecture_message_text(item: Union[Series, DataFrame]) -> str:
    if isinstance(item.series, str):
        series_text, lecture = item.series, item.lecture
    else:
        series_text, lecture = item.series.item(), item.lecture.item()
    return f"السلسلة: <b> 🗂{series_text}</b>\n📚 الدرس: <b>{lecture}</b>\n"


def get_data(
    data: Series, data_column_id: str, page: int = 1
) -> Tuple[str, InlineKeyboardMarkup]:
    text = "*اختر ما تريد من القائمة:*"
    paginator = InlineKeyboardPaginator(
        round(len(data) / page_size),
        current_page=page,
        data_pattern=f"list_{data_column_id}#{page}",
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
def data_command_handler(
    update: Update, _: CallbackContext, data_column_id: str = "series"
) -> None:
    text, reply_markup = get_data(getattr(sheet, data_column_id), data_column_id)
    update.message.reply_text(text, reply_markup=reply_markup)


@tg_exceptions_handler
def data_callback_handler(update: Update, _: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    data_column_id = query.data.split("_")[-1].split("#")[0]
    current_page_callback_value = query.data.split("#")[1]
    current_page = (
        int(current_page_callback_value) if current_page_callback_value else 1
    )
    text, reply_markup = get_data(
        getattr(sheet, data_column_id), data_column_id, page=current_page
    )
    query.edit_message_text(
        text=text,
        reply_markup=reply_markup,
    )


@tg_exceptions_handler
def droos_handler(update: Update, _: CallbackContext) -> None:
    """Sends Droos list."""
    query = update.callback_query
    query.answer()
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
        query.edit_message_text(
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
        series_data: Series = data.groupby(f"series_slug")["series"].unique()
        text, reply_markup = get_data(series_data, "series", page=page_idx)
        query.edit_message_text(
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
    query.edit_message_text(
        text=get_lecture_message_text(item),
        reply_markup=paginator.markup,
        parse_mode=ParseMode.HTML,
    )


@tg_exceptions_handler
@analysis
def get_lecture_callback_handler(
    update: Update, _: CallbackContext
) -> Optional[Series]:
    query = update.callback_query
    query.answer()
    __, data, lecture_id = query.data.split("|")
    lecture_info = sheet.df[sheet.df.id == lecture_id]
    if lecture_info.empty or getattr(lecture_info, data).empty:
        return None
    media = getattr(lecture_info, data).item()
    media_type, info = media.split("τ")
    file_id, caption = info.split("Ͱ")
    text = caption if caption else get_lecture_message_text(lecture_info)
    if media_type == "text":
        dispatcher.bot.send_message(
            chat_id=query.message.chat_id,
            text=caption,
            parse_mode=ParseMode.HTML,
        )
    if media_type == "video":
        dispatcher.bot.send_video(
            chat_id=query.message.chat_id,
            video=file_id,
            caption=text,
            parse_mode=ParseMode.HTML,
        )
    elif media_type == "audio":
        dispatcher.bot.send_audio(
            chat_id=query.message.chat_id,
            audio=file_id,
            caption=text,
            parse_mode=ParseMode.HTML,
        )
    elif media_type == "voice":
        dispatcher.bot.send_voice(
            chat_id=query.message.chat_id,
            voice=file_id,
            caption=text,
            parse_mode=ParseMode.HTML,
        )
    elif media_type == "document":
        dispatcher.bot.send_document(
            chat_id=query.message.chat_id,
            document=file_id,
            caption=text,
            parse_mode=ParseMode.HTML,
        )
    elif media_type == "photo":
        dispatcher.bot.send_photo(
            chat_id=query.message.chat_id,
            photo=file_id,
            caption=text,
            parse_mode=ParseMode.HTML,
        )
    return lecture_info


# series
for _data_column_id, _data_column_name in DATA_COLUMNS.items():
    dispatcher.add_handler(
        MessageHandler(
            Filters.regex(_data_column_name),
            partial(data_command_handler, data_column_id=_data_column_id),
        )
    )
    dispatcher.add_handler(
        CallbackQueryHandler(data_callback_handler, pattern=r"^list_[\w]+#")
    )
    # lectures
    dispatcher.add_handler(
        CallbackQueryHandler(droos_handler, pattern=r"^load_[\w]+\|")
    )
    dispatcher.add_handler(CallbackQueryHandler(droos_handler, pattern=r"^[\w_]+#"))
dispatcher.add_handler(
    CallbackQueryHandler(get_lecture_callback_handler, pattern=r"^getd\|")
)
