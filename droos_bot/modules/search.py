"""Data search module."""

from typing import cast

from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from droos_bot import application, sheet
from droos_bot.modules.droos import get_data
from droos_bot.utils.keyboards import cancel_search_keyboard, main_keyboard
from droos_bot.utils.telegram import tg_exceptions_handler

START_SEARCH = 0


@tg_exceptions_handler
async def search_handler(update: Update, _: ContextTypes.DEFAULT_TYPE) -> int:
    assert update.effective_message is not None
    await update.message.reply_text(
        "اكتب ما تريد البحث عنه",
        reply_to_message_id=update.effective_message.message_id,
        reply_markup=cancel_search_keyboard,
    )
    return START_SEARCH


@tg_exceptions_handler
async def search_for_text(update: Update, _: ContextTypes.DEFAULT_TYPE) -> int | None:
    assert update.effective_message is not None
    search_text = update.effective_message.text.strip()
    match = (
        sheet.df[sheet.df.series.str.contains(search_text)]
        .groupby("series_slug")["series"]
        .unique()
    )
    if match.empty:
        await update.message.reply_text(
            "لا يوجد نتائج", reply_to_message_id=update.effective_message.message_id
        )
        return None

    text, reply_markup = get_data(match, "series")
    await update.message.reply_text(
        text,
        reply_markup=reply_markup,
        reply_to_message_id=update.effective_message.message_id,
    )
    await cancel_search_handler(update, _)
    return cast(int, ConversationHandler.END)


async def cancel_search_handler(update: Update, _: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "يمكنك متابعة استخدام البوت من خلال الأزرار الظاهرة بالأسفل",
        reply_markup=main_keyboard,
    )
    return cast(int, ConversationHandler.END)


search_conversation_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^البحث عن سلسلة$"), search_handler)],
    states={
        START_SEARCH: [
            MessageHandler(
                filters.TEXT
                & ~(
                    filters.COMMAND
                    | filters.Regex("^البحث عن سلسلة$")
                    | filters.Regex("^إلغاء البحث$")
                ),
                search_for_text,
            )
        ],
    },
    fallbacks=[
        CommandHandler("cancel", cancel_search_handler),
        MessageHandler(filters.Regex("^إلغاء البحث$"), cancel_search_handler),
    ],
)

application.add_handler(search_conversation_handler)
