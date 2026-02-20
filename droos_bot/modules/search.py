"""Data search module."""

from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from droos_bot import DATA_COLUMNS, application, sheet
from droos_bot.utils.keyboards import cancel_search_keyboard, create_keyboard, main_keyboard
from droos_bot.utils.telegram import tg_exceptions_handler

START_SEARCH = 0
BOT_COMMANDS = [("cancel", "إلغاء العملية الحالية", "user")]


@tg_exceptions_handler
async def search_handler(update: Update, _: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.effective_message
    assert message is not None
    await message.reply_text(
        "اكتب ما تريد البحث عنه",
        reply_to_message_id=message.message_id,
        reply_markup=cancel_search_keyboard,
    )
    return START_SEARCH


@tg_exceptions_handler
async def search_for_text(update: Update, _: ContextTypes.DEFAULT_TYPE) -> int | None:
    message = update.effective_message
    assert message is not None
    assert message.text is not None
    search_text = message.text.strip()
    match = sheet.df[
        sheet.df[list(DATA_COLUMNS.keys())]
        .astype(str)
        .apply(lambda x: x.str.contains(search_text, case=False, regex=True, na=False))
        .any(axis=1)
    ]
    if match.empty:
        await message.reply_text("لا يوجد نتائج", reply_to_message_id=message.message_id)
        return None
    melted = match.melt(
        id_vars=["id"], value_vars=list(DATA_COLUMNS.keys()), var_name="column", value_name="value"
    )
    melted = melted[melted["value"].notna()]
    grouped_results = {
        DATA_COLUMNS[k]: v.tolist()
        for k, v in melted.groupby("column")["value"].unique().to_dict().items()
    }
    reply_markup = create_keyboard(
        [
            f"{key} > {value}"
            for key, values in reversed(grouped_results.items())
            for value in values
        ],
        show_back=False,
        show_pagination=False,
    )
    await message.reply_text(
        "نتائج البحث:",
        reply_markup=reply_markup,
        reply_to_message_id=message.message_id,
    )
    return ConversationHandler.END


async def cancel_search_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.effective_message
    assert message is not None
    user_data = context.user_data
    assert user_data is not None
    user_data["path"] = []
    await message.reply_text(
        "يمكنك متابعة استخدام البوت من خلال الأزرار الظاهرة بالأسفل",
        reply_markup=main_keyboard,
    )
    return ConversationHandler.END


application.add_handler(
    ConversationHandler(
        entry_points=[
            MessageHandler(
                filters.Regex("^البحث في المحتوى$"),
                search_handler,  # ty: ignore[invalid-argument-type]
            )
        ],
        states={
            START_SEARCH: [
                MessageHandler(
                    filters.ChatType.PRIVATE
                    & filters.TEXT
                    & ~(
                        filters.COMMAND
                        | filters.Regex("^البحث في المحتوى$")
                        | filters.Regex("^إلغاء البحث$")
                    ),
                    search_for_text,  # ty: ignore[invalid-argument-type]
                )
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_search_handler, filters.ChatType.PRIVATE),
            MessageHandler(
                filters.ChatType.PRIVATE & filters.Regex("^إلغاء البحث$"),
                cancel_search_handler,
            ),
            MessageHandler(
                filters.ChatType.PRIVATE & filters.Regex("^(القائمة الرئيسية 🏠)$"),
                cancel_search_handler,
            ),
        ],
    )
)
