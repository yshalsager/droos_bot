"""
Data search module
"""
from typing import Optional

from telegram import Update
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    ConversationHandler,
    Filters,
    MessageHandler,
)

from droos_bot import dispatcher, sheet
from droos_bot.modules.droos import get_data
from droos_bot.utils.keyboards import cancel_search_keyboard, main_keyboard
from droos_bot.utils.telegram import tg_exceptions_handler

START_SEARCH = 0


@tg_exceptions_handler
def search_handler(update: Update, _: CallbackContext) -> int:
    assert update.effective_message is not None
    update.message.reply_text(
        "اكتب ما تريد البحث عنه",
        reply_to_message_id=update.effective_message.message_id,
        reply_markup=cancel_search_keyboard,
    )
    return START_SEARCH


@tg_exceptions_handler
def search_for_text(update: Update, _: CallbackContext) -> Optional[int]:
    assert update.effective_message is not None
    search_text = update.effective_message.text.strip()
    match = (
        sheet.df[sheet.df.series.str.contains(search_text)]
        .groupby("series_slug")["series"]
        .unique()
    )
    if match.empty:
        update.message.reply_text(
            "لا يوجد نتائج", reply_to_message_id=update.effective_message.message_id
        )
        return None

    text, reply_markup = get_data(match, "series")
    update.message.reply_text(
        text,
        reply_markup=reply_markup,
        reply_to_message_id=update.effective_message.message_id,
    )
    cancel_search_handler(update, _)
    return ConversationHandler.END


def cancel_search_handler(update: Update, _: CallbackContext) -> int:
    update.message.reply_text(
        "يمكنك متابعة استخدام البوت من خلال الأزرار الظاهرة بالأسفل",
        reply_markup=main_keyboard,
    )
    return ConversationHandler.END


search_conversation_handler = ConversationHandler(
    entry_points=[MessageHandler(Filters.regex("^البحث عن سلسلة$"), search_handler)],
    states={
        START_SEARCH: [
            MessageHandler(
                Filters.text
                & ~(
                    Filters.command
                    | Filters.regex("^البحث عن سلسلة$")
                    | Filters.regex("^إلغاء البحث$")
                ),
                search_for_text,
            )
        ],
    },
    fallbacks=[
        CommandHandler("cancel", cancel_search_handler),
        MessageHandler(Filters.regex("^إلغاء البحث$"), cancel_search_handler),
    ],
)

dispatcher.add_handler(search_conversation_handler)
