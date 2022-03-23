"""
Feedback and files handler module.
"""
import re

from telegram import ParseMode, Update
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    ConversationHandler,
    Filters,
    MessageHandler,
)

from droos_bot import CONFIG, dispatcher
from droos_bot.modules.search import cancel_search_handler
from droos_bot.utils.filters import FeedbackMessageFilter
from droos_bot.utils.keyboards import cancel_keyboard
from droos_bot.utils.telegram import tg_exceptions_handler

START_RECEIVING_FEEDBACK = 1
START_RECEIVING_FILES = 2
notice_message = (
    "بعد الانتهاء اضغط على زر إنهاء الموجود بالأسفل\n"
    "إذا كنت ترغب في أن نتواصل معك رجاء اترك معرف أو رابط حساب ليتواصل معك المشرفون من خلاله إن شاء الله "
    "إذا كان معرف حسابك لا يظهر عند إعادة توجيه الرسائل"
)


@tg_exceptions_handler
def feedback_handler(update: Update, _: CallbackContext) -> int:
    """Handle feedback from users."""
    assert update.effective_message is not None
    update.message.reply_text(
        "يمكنك كتابة ما تريد إرساله للمشرفين على البوت هنا\n" + notice_message,
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
        "يمكنك إرسال مواد لإضافتها للبوت هنا\n" + notice_message,
        reply_to_message_id=update.effective_message.message_id,
        reply_markup=cancel_keyboard,
    )
    return START_RECEIVING_FILES


@tg_exceptions_handler
def reply_to_feedback(update: Update, context: CallbackContext) -> None:
    assert update.effective_message is not None
    assert context.match is not None
    # Handle the update if the message replied to is forwarded from the bot itself only
    if not update.effective_message.reply_to_message.from_user.id == context.bot.id:
        return
    if not update.effective_message.reply_to_message.forward_from:
        update.effective_message.reply_text(
            "لا يمكن الرد على هذا المستخدم بسبب إعدادات حسابه",
            reply_to_message_id=update.effective_message.message_id,
        )
        return
    replied_to_message_text = update.effective_message.reply_to_message.text_html_urled
    admin_reply_message_text = update.effective_message.text_html_urled.replace(
        context.match.group(1), ""
    ).strip()
    reply_with_message_text = (
        f"<b>رسالتك:</b>\n{replied_to_message_text}\n\n"
        f"<b>رد المشرف</b>:\n{admin_reply_message_text}\n\n"
        f"<b>ملاحظة</b>:\nللرد على هذه الرسالة اضغط على زر التواصل والاقتراحات أولا ثم أرسل الرد"
    )
    # TODO handle a case when message text is >= telegram.MAX_MESSAGE_LENGTH
    context.bot.send_message(
        update.effective_message.reply_to_message.forward_from.id,
        reply_with_message_text,
        parse_mode=ParseMode.HTML,
    )
    admin_message = (
        f'<a href="{update.effective_message.reply_to_message.link}">رُد</a> على '
        f'<a href="tg://user?id={update.effective_message.reply_to_message.forward_from.id}">'
        f"{update.effective_message.reply_to_message.forward_from.full_name}</a> بـ:\n"
        f"{admin_reply_message_text}"
    )
    update.effective_message.reply_text(
        admin_message,
        reply_to_message_id=update.effective_message.message_id,
        parse_mode=ParseMode.HTML,
    )


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

filter_feedback_message = FeedbackMessageFilter(CONFIG["tg_feedback_chat_id"])
dispatcher.add_handler(
    MessageHandler(
        Filters.regex(re.compile(r"^(/reply|/r)\s+([\S\s]+)$", re.M))
        & filter_feedback_message,
        reply_to_feedback,
    )
)
