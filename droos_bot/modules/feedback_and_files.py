"""
Feedback and files handler module.
"""
from telegram import Update
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    ConversationHandler,
    Filters,
    MessageHandler,
)

from droos_bot import CONFIG, dispatcher
from droos_bot.modules.search import cancel_search_handler
from droos_bot.utils.keyboards import cancel_keyboard
from droos_bot.utils.telegram import tg_exceptions_handler

START_RECEIVING_FEEDBACK = 1
START_RECEIVING_FILES = 2


@tg_exceptions_handler
def feedback_handler(update: Update, _: CallbackContext) -> int:
    """Handle feedback from users."""
    assert update.effective_message is not None
    update.message.reply_text(
        "يمكنك كتابة ما تريد إرساله للمشرفين على البوت هنا\nبعد الانتهاء اضغط على زر إنهاء الموجود بالأسفل",
        reply_to_message_id=update.effective_message.message_id,
        reply_markup=cancel_keyboard,
    )
    return START_RECEIVING_FEEDBACK


@tg_exceptions_handler
def forward_feedback(update: Update, context: CallbackContext) -> None:
    assert update.effective_message is not None
    assert update.effective_chat is not None
    context.bot.forward_message(
        chat_id=CONFIG["tg_feedback_chat_id"],
        from_chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id,
    )
    update.message.reply_text(
        r"تم استلام رسالتك بنجاح\. بإمكانك إرسال المزيد أو الضغط على زر إنهاء للعودة"
    )


@tg_exceptions_handler
def files_handler(update: Update, _: CallbackContext) -> int:
    """Handle files from users."""
    assert update.effective_message is not None
    update.message.reply_text(
        "يمكنك إرسال مواد لإضافتها للبوت هنا\nبعد الانتهاء اضغط على زر إنهاء الموجود بالأسفل",
        reply_to_message_id=update.effective_message.message_id,
        reply_markup=cancel_keyboard,
    )
    return START_RECEIVING_FILES


feedback_conversation_handler = ConversationHandler(
    entry_points=[
        MessageHandler(Filters.regex("^التواصل والاقتراحات$"), feedback_handler)
    ],
    states={
        START_RECEIVING_FEEDBACK: [
            MessageHandler(
                Filters.text
                & ~(
                    Filters.command
                    | Filters.regex("^التواصل والاقتراحات$")
                    | Filters.regex("^إنهاء$")
                ),
                forward_feedback,
            )
        ],
    },
    fallbacks=[
        CommandHandler("cancel", cancel_search_handler),
        MessageHandler(Filters.regex("^إنهاء$"), cancel_search_handler),
    ],
)

files_conversation_handler = ConversationHandler(
    entry_points=[MessageHandler(Filters.regex("^إرسال مواد$"), files_handler)],
    states={
        START_RECEIVING_FILES: [
            MessageHandler(
                Filters.photo | Filters.video | Filters.audio | Filters.document,
                forward_feedback,
            )
        ],
    },
    fallbacks=[
        CommandHandler("cancel", cancel_search_handler),
        MessageHandler(Filters.regex("^إنهاء$"), cancel_search_handler),
    ],
)

dispatcher.add_handler(feedback_conversation_handler)
dispatcher.add_handler(files_conversation_handler)
