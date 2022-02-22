from telegram import Update
from telegram.ext import CallbackContext, Filters, MessageHandler

from droos_bot import dispatcher, sheet
from droos_bot.modules.droos import get_series
from droos_bot.utils.filters import SearchTextFilter
from droos_bot.utils.telegram import tg_exceptions_handler

search_reply_text = "اكتب ما تريد البحث عنه في رد على هذه الرسالة"


@tg_exceptions_handler
def search_handler(update: Update, _: CallbackContext) -> None:
    update.message.reply_text(
        search_reply_text, reply_to_message_id=update.effective_message.message_id
    )


@tg_exceptions_handler
def search_for_text(update: Update, _: CallbackContext) -> None:
    search_text = update.effective_message.text.strip()
    match = (
        sheet.df[sheet.df.series.str.contains(search_text)]
        .groupby("slug")["series"]
        .unique()
    )
    if match.empty:
        update.message.reply_text(
            "لا يوجد نتائج", reply_to_message_id=update.effective_message.message_id
        )
        return

    text, reply_markup = get_series(match)
    update.message.reply_text(
        text,
        reply_markup=reply_markup,
        reply_to_message_id=update.effective_message.message_id,
    )


dispatcher.add_handler(MessageHandler(Filters.regex("البحث عن سلسلة"), search_handler))
filter_search_text = SearchTextFilter(search_reply_text)
dispatcher.add_handler(MessageHandler(filter_search_text, search_for_text))
