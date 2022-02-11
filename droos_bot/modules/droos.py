"""
Droos handler module.
"""

from pandas import Series, DataFrame
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler
from telegram.utils.helpers import escape_markdown
from telegram_bot_pagination import InlineKeyboardPaginator

from droos_bot import dispatcher, sheet
from droos_bot.utils.telegram import tg_exceptions_handler


def get_lecture_message_text(item: Series) -> str:
    if isinstance(item.series, str):
        return f"السلسلة: *{item.series}*\nالدرس: *{item.lecture}*\n"
    return f"السلسلة: *{item.series.item()}*\nالدرس: *{item.lecture.item()}*\n"


def get_series() -> (str, InlineKeyboardMarkup):
    text = "السلاسل المتوفرة"
    keyboard = []
    for series, slug in sheet.series.items():
        keyboard.append([InlineKeyboardButton(series, callback_data=f"gets|{slug[0]}")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    return text, reply_markup


@tg_exceptions_handler
def series_command_handler(update: Update, _: CallbackContext) -> None:
    text, reply_markup = get_series()
    update.message.reply_text(text, reply_markup=reply_markup)


@tg_exceptions_handler
def series_callback_handler(update: Update, _: CallbackContext) -> None:
    text, reply_markup = get_series()
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text=text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN_V2,
    )


@tg_exceptions_handler
def droos_handler(update: Update, _: CallbackContext) -> None:
    """Sends Droos list."""
    query = update.callback_query
    query.answer()
    if "|" in query.data:
        series_slug = query.data.split("|")[1]
        page_idx = 1
    else:
        series_slug = query.data.split("#")[0]
        page_idx = int(query.data.split("#")[1])
    series: DataFrame = sheet.df[sheet.df.slug == series_slug]
    item: Series = series.iloc[page_idx - 1, :]
    paginator = InlineKeyboardPaginator(
        len(series), current_page=page_idx, data_pattern=series_slug + "#{page}"
    )
    buttons = []
    if item.main:
        buttons.append(
            InlineKeyboardButton("📝أهم المحاور", callback_data=f"getd|main|{item.id}")
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
    paginator.add_after(InlineKeyboardButton("رجوع", callback_data="list_series"))
    query.edit_message_text(
        text=get_lecture_message_text(item),
        reply_markup=paginator.markup,
        parse_mode=ParseMode.MARKDOWN_V2,
        disable_web_page_preview=True,
    )


@tg_exceptions_handler
def get_lecture_callback_handler(update: Update, _: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    _, data, lecture_id = query.data.split("|")
    lecture_info = sheet.df[sheet.df.id == lecture_id]
    if lecture_info.empty or getattr(lecture_info, data).empty:
        return
    media = getattr(lecture_info, data).item()
    media_type, info = media.split("τ")
    file_id, caption = info.split("Ͱ")
    text = caption if caption else get_lecture_message_text(lecture_info)
    text = escape_markdown(text, version=2)
    if media_type == "video":
        dispatcher.bot.send_video(
            chat_id=query.message.chat_id,
            video=file_id,
            caption=text,
            parse_mode=ParseMode.MARKDOWN_V2,
        )
    elif media_type == "audio":
        dispatcher.bot.send_audio(
            chat_id=query.message.chat_id,
            audio=file_id,
            caption=text,
            parse_mode=ParseMode.MARKDOWN_V2,
        )
    elif media_type == "voice":
        dispatcher.bot.send_voice(
            chat_id=query.message.chat_id,
            voice=file_id,
            caption=text,
            parse_mode=ParseMode.MARKDOWN_V2,
        )
    elif media_type == "document":
        dispatcher.bot.send_document(
            chat_id=query.message.chat_id,
            document=file_id,
            caption=text,
            parse_mode=ParseMode.MARKDOWN_V2,
        )
    elif media_type == "photo":
        dispatcher.bot.send_photo(
            chat_id=query.message.chat_id,
            photo=file_id,
            caption=text,
            parse_mode=ParseMode.MARKDOWN_V2,
        )


# series
dispatcher.add_handler(CommandHandler("series", series_command_handler, run_async=True))
dispatcher.add_handler(
    CallbackQueryHandler(
        series_callback_handler, pattern=r"^list_series", run_async=True
    )
)
# lectures
dispatcher.add_handler(
    CallbackQueryHandler(droos_handler, pattern=r"^gets\|", run_async=True)
)
dispatcher.add_handler(
    CallbackQueryHandler(droos_handler, pattern=r"^[\w_]+#", run_async=True)
)
dispatcher.add_handler(
    CallbackQueryHandler(
        get_lecture_callback_handler, pattern=r"^getd\|", run_async=True
    )
)
