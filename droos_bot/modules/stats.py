"""Bot stats module."""

from pandas import DataFrame
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CommandHandler, ContextTypes

from droos_bot import application, sheet
from droos_bot.db import Lecture, Series
from droos_bot.db.curd import (
    get_chats_count,
    get_top_lectures,
    get_top_series,
    get_usage_count,
)
from droos_bot.utils.filters import FilterBotAdmin


async def stats(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    stats_message = await update.message.reply_text("جاري تحضير الإحصائيات…")
    all_chats, active_chats = get_chats_count()
    usage_times, series_requests, lecture_requests = get_usage_count()
    top_series: list[Series] = get_top_series()
    top_lectures: list[Lecture] = get_top_lectures()

    message = (
        f"**المستخدمون الحاليون**: {active_chats!s}\n"
        f"**كل المستخدمون**: {all_chats!s}\n"
        f"**إجمالي مرات الاستخدام**: {usage_times!s}\n"
        f"**إجمالي الملفات المرسلة**: {series_requests!s}\n"
        f"**إجمالي الدروس المطلوبة**: {lecture_requests!s}\n\n"
        f"**أكثر السلاسل طلبًا**:\n"
        f"$top_series\n"
        f"**أكثر الدروس طلبًا**:\n"
        f"$top_lectures\n"
    )
    top_series_message = ""
    if top_series:
        for series in top_series:
            try:
                top_series_message += f"  `{sheet.df[sheet.df.series_slug == series.id].iloc[0].series}`: {series.requests!s} مرة\n"
            except IndexError:
                continue
    top_lectures_message = ""
    if top_lectures:
        for lecture in top_lectures:
            try:
                lecture_info: DataFrame = sheet.df[sheet.df.id == lecture.id]
                top_lectures_message += f"  `{lecture_info.series.item()} ({lecture_info.lecture.item()})`: {lecture.requests!s} مرة\n"
            except ValueError:
                continue
    message = message.replace("$top_series", top_series_message).replace(
        "$top_lectures", top_lectures_message
    )

    await stats_message.edit_text(message, parse_mode=ParseMode.MARKDOWN_V2)


filter_bot_admin = FilterBotAdmin()
application.add_handler(CommandHandler("stats", stats, filter_bot_admin))
