"""
Droos handler module.
"""
from typing import Optional, Tuple, Union

from pandas import DataFrame, Series
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.ext import CallbackContext, CallbackQueryHandler, Filters, MessageHandler
from telegram_bot_pagination import InlineKeyboardPaginator

from droos_bot import dispatcher, sheet
from droos_bot.utils.analytics import add_new_chat_to_db, analysis
from droos_bot.utils.telegram import tg_exceptions_handler

page_size = 5


def get_lecture_message_text(item: Union[Series, DataFrame]) -> str:
    if isinstance(item.series, str):
        series_text, lecture = item.series, item.lecture
    else:
        series_text, lecture = item.series.item(), item.lecture.item()
    return f"السلسلة: <b> 🗂{series_text}</b>\n📚 الدرس: <b>{lecture}</b>\n"


def get_series(series: Series, page: int = 1) -> Tuple[str, InlineKeyboardMarkup]:
    text = "*السلاسل المتوفرة*"
    paginator = InlineKeyboardPaginator(
        round(len(series) / page_size),
        current_page=page,
        data_pattern="list_series#{page}",
    )
    chunk_start: int = (page - 1) * page_size
    series_list = series.iloc[chunk_start : chunk_start + page_size]
    for slug, series_ in series_list.iteritems():
        paginator.add_before(
            InlineKeyboardButton(series_.item(), callback_data=f"gets|{slug}")
        )
    return text, paginator.markup


@tg_exceptions_handler
@add_new_chat_to_db
def series_command_handler(update: Update, _: CallbackContext) -> None:
    text, reply_markup = get_series(sheet.series)
    update.message.reply_text(text, reply_markup=reply_markup)


@tg_exceptions_handler
def series_callback_handler(update: Update, _: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    current_page = 1
    current_page_callback_value = query.data.split("#")[1]
    if current_page_callback_value:
        current_page = int(current_page_callback_value)
    text, reply_markup = get_series(sheet.series, page=current_page)
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
    if "|" in query.data:
        series_slug = query.data.split("|")[1]
        page_idx = 1
    else:
        # lecture query
        series_slug = query.data.split("#")[0]
        page_idx = int(query.data.split("#")[1])
    series: DataFrame = sheet.df[sheet.df.slug == series_slug]
    item: Series = series.iloc[page_idx - 1, :]
    paginator = InlineKeyboardPaginator(
        len(series), current_page=page_idx, data_pattern=series_slug + "#{page}"
    )
    buttons = []
    if item.book:
        buttons.append(
            InlineKeyboardButton("📕 الكتاب", callback_data=f"getd|book|{item.id}")
        )
    if item.main:
        buttons.append(
            InlineKeyboardButton("📝 المحاور", callback_data=f"getd|main|{item.id}")
        )
    if item.video:
        buttons.append(
            InlineKeyboardButton("🎞 فيديو", callback_data=f"getd|video|{item.id}")
        )
    if item.voice:
        buttons.append(
            InlineKeyboardButton("🎧 صوتي", callback_data=f"getd|voice|{item.id}")
        )
    if item.text:
        buttons.append(
            InlineKeyboardButton("📄 تفريغ", callback_data=f"getd|text|{item.id}")
        )
    if item.summary:
        buttons.append(
            InlineKeyboardButton("📎 ملخص", callback_data=f"getd|summary|{item.id}")
        )
    paginator.add_before(*buttons)
    paginator.add_after(InlineKeyboardButton("رجوع", callback_data="list_series#"))
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
dispatcher.add_handler(
    MessageHandler(Filters.regex("^السلاسل العلمية$"), series_command_handler)
)
dispatcher.add_handler(
    CallbackQueryHandler(series_callback_handler, pattern=r"^list_series#")
)
# lectures
dispatcher.add_handler(CallbackQueryHandler(droos_handler, pattern=r"^gets\|"))
dispatcher.add_handler(CallbackQueryHandler(droos_handler, pattern=r"^[\w_]+#"))
dispatcher.add_handler(
    CallbackQueryHandler(get_lecture_callback_handler, pattern=r"^getd\|")
)
