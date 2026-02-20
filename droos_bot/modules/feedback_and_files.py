"""Feedback and files handler module."""

from telegram import MessageOriginHiddenUser, MessageOriginUser, Update
from telegram.constants import MessageLimit
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from droos_bot import CONFIG, application
from droos_bot.db.curd import get_chat_id_by_name
from droos_bot.modules.search import cancel_search_handler
from droos_bot.utils.filters import FeedbackMessageFilter, FilterBotAdmin
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
async def feedback_handler(update: Update, _: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle feedback from users."""
    message = update.effective_message
    assert message is not None
    await message.reply_text(
        "يمكنك كتابة ما تريد إرساله للمشرفين على البوت هنا\n" + notice_message,
        reply_to_message_id=message.message_id,
        reply_markup=cancel_keyboard,
    )
    return START_RECEIVING_FEEDBACK


@tg_exceptions_handler
async def forward_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    assert message is not None
    assert update.effective_chat is not None
    await context.bot.forward_message(
        chat_id=CONFIG["tg_feedback_chat_id"],
        from_chat_id=update.effective_chat.id,
        message_id=message.message_id,
    )
    await message.reply_text(
        r"تم استلام رسالتك بنجاح\. بإمكانك إرسال المزيد أو الضغط على زر إنهاء للعودة"
    )


@tg_exceptions_handler
async def files_handler(update: Update, _: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle files from users."""
    message = update.effective_message
    assert message is not None
    await message.reply_text(
        "يمكنك إرسال مواد لإضافتها للبوت هنا\n" + notice_message,
        reply_to_message_id=message.message_id,
        reply_markup=cancel_keyboard,
    )
    return START_RECEIVING_FILES


@tg_exceptions_handler
async def reply_to_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    assert message is not None
    assert update.effective_chat is not None
    reply_to_message = message.reply_to_message
    assert reply_to_message is not None
    forward_origin = reply_to_message.forward_origin
    if forward_origin and isinstance(forward_origin, MessageOriginHiddenUser):
        if not forward_origin.sender_user_name:
            await message.reply_text(
                "لا يمكن الرد على هذا المستخدم بسبب إعدادات حسابه",
                reply_to_message_id=message.message_id,
            )
            return
        chat_id = get_chat_id_by_name(forward_origin.sender_user_name)
        if not chat_id:
            await message.reply_text(
                "لا يمكن الرد على هذا المستخدم بسبب إعدادات حسابه",
                reply_to_message_id=message.message_id,
            )
            return
    elif not forward_origin:
        if reply_to_message.from_user and reply_to_message.from_user.is_bot:
            return
        return
    else:
        assert isinstance(forward_origin, MessageOriginUser)
        chat_id = forward_origin.sender_user.id
    replied_to_message_text = reply_to_message.text_html_urled or ""
    reply_with_message_text = (
        f"<b>رد المشرف على رسالتك السابقة:</b>\n\n{replied_to_message_text[: MessageLimit.MAX_TEXT_LENGTH - 150]}\n\n"
        f"<b>ملاحظة</b>:\nللرد على هذه الرسالة اضغط على زر التواصل والاقتراحات أولا ثم أرسل الرد"
    )
    await context.bot.send_message(
        chat_id,
        reply_with_message_text,
    )
    await context.bot.copy_message(
        chat_id=chat_id,
        from_chat_id=update.effective_chat.id,
        message_id=message.message_id,
    )
    sender_name = (
        forward_origin.sender_user_name
        if isinstance(forward_origin, MessageOriginHiddenUser)
        else forward_origin.sender_user.full_name
    )
    admin_message = (
        f'<a href="{reply_to_message.link}">رُد</a> على '
        f'<a href="tg://user?id={chat_id}">'
        f"{sender_name}</a> "
        f'<a href="{message.link}">بهذا الرد</a>'
    )
    await message.reply_text(
        admin_message,
        reply_to_message_id=message.message_id,
    )


feedback_conversation_handler = ConversationHandler(
    entry_points=[
        MessageHandler(
            filters.Regex("^التواصل والاقتراحات$"),
            feedback_handler,  # ty: ignore[invalid-argument-type]
        )
    ],
    states={
        START_RECEIVING_FEEDBACK: [
            MessageHandler(
                filters.TEXT
                & ~(
                    filters.COMMAND
                    | filters.Regex("^التواصل والاقتراحات$")
                    | filters.Regex("^إنهاء$")
                ),
                forward_feedback,  # ty: ignore[invalid-argument-type]
            )
        ],
    },
    fallbacks=[  # ty: ignore[invalid-argument-type]
        CommandHandler("cancel", cancel_search_handler),
        MessageHandler(filters.Regex("^إنهاء$"), cancel_search_handler),
    ],
)

files_conversation_handler = ConversationHandler(
    entry_points=[
        MessageHandler(
            filters.Regex("^إرسال مواد$"),
            files_handler,  # ty: ignore[invalid-argument-type]
        )
    ],
    states={
        START_RECEIVING_FILES: [
            MessageHandler(
                filters.PHOTO | filters.VIDEO | filters.AUDIO | filters.Document.ALL,
                forward_feedback,  # ty: ignore[invalid-argument-type]
            )
        ],
    },
    fallbacks=[  # ty: ignore[invalid-argument-type]
        CommandHandler("cancel", cancel_search_handler),
        MessageHandler(filters.Regex("^إنهاء$"), cancel_search_handler),
    ],
)

if "التواصل والاقتراحات" not in CONFIG.get("disable", []):
    application.add_handler(feedback_conversation_handler)
if "إرسال مواد" not in CONFIG.get("disable", []):
    application.add_handler(files_conversation_handler)

filter_feedback_message = FeedbackMessageFilter(
    CONFIG["tg_feedback_chat_id"], CONFIG["tg_bot_token"].split(":")[0]
)
application.add_handler(
    MessageHandler(
        FilterBotAdmin() & filter_feedback_message,
        reply_to_feedback,  # ty: ignore[invalid-argument-type]
    )
)
