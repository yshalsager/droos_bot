# """ Bot stats module"""
from typing import List

from pandas import DataFrame
from telegram import ParseMode, Update
from telegram.ext import CallbackContext, CommandHandler

from droos_bot import dispatcher, sheet
from droos_bot.db import Lecture, Series
from droos_bot.db.curd import (
    get_chats_count,
    get_top_lectures,
    get_top_series,
    get_usage_count,
)
from droos_bot.utils.filters import FilterBotAdmin


def stats(update: Update, _: CallbackContext) -> None:
    stats_message = update.message.reply_text("جاري تحضير الإحصائيات…")
    all_chats, active_chats = get_chats_count()
    usage_times, series_requests, lecture_requests = get_usage_count()
    top_series: List[Series] = get_top_series()
    top_lectures: List[Lecture] = get_top_lectures()

    message = (
        f"**المستخدمون الحاليون**: {str(active_chats)}\n"
        f"**كل المستخدمون**: {str(all_chats)}\n"
        f"**إجمالي مرات الاستخدام**: {str(usage_times)}\n"
        f"**إجمالي الملفات المرسلة**: {str(series_requests)}\n"
        f"**إجمالي الدروس المطلوبة**: {str(lecture_requests)}\n\n"
        f"**أكثر السلاسل طلبًا**:\n"
        f"$top_series\n"
        f"**أكثر الدروس طلبًا**:\n"
        f"$top_lectures\n"
    )
    top_series_message = ""
    if top_series:
        for series in top_series:
            try:
                top_series_message += f"  `{sheet.df[sheet.df.series_slug == series.id].iloc[0].series}`: {str(series.requests)} مرة\n"
            except IndexError:
                continue
    top_lectures_message = ""
    if top_lectures:
        for lecture in top_lectures:
            try:
                lecture_info: DataFrame = sheet.df[sheet.df.id == lecture.id]
                top_lectures_message += f"  `{lecture_info.series.item()} ({lecture_info.lecture.item()})`: {str(lecture.requests)} مرة\n"
            except ValueError:
                continue
    message = message.replace("$top_series", top_series_message).replace(
        "$top_lectures", top_lectures_message
    )

    stats_message.edit_text(message, parse_mode=ParseMode.MARKDOWN_V2)


filter_bot_admin = FilterBotAdmin()
dispatcher.add_handler(CommandHandler("stats", stats, filter_bot_admin))
