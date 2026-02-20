"""broadcast module."""

import logging
from asyncio import sleep

from telegram import Update
from telegram.error import TelegramError
from telegram.ext import CommandHandler, ContextTypes, filters

from droos_bot import application
from droos_bot.db.curd import get_all_chats
from droos_bot.utils.filters import FilterBotAdmin
from droos_bot.utils.telegram import tg_exceptions_handler

logger = logging.getLogger(__name__)
BOT_COMMANDS = [("broadcast", "إرسال رسالة جماعية", "admin")]


@tg_exceptions_handler
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Broadcasts message to bot users."""
    message = update.effective_message
    assert message is not None
    assert update.effective_chat is not None
    message_to_send = message.reply_to_message
    assert message_to_send is not None
    failed_to_send = 0
    sent_successfully = 0
    for chat in get_all_chats():
        try:
            await context.bot.copy_message(
                chat_id=int(chat.user_id),
                from_chat_id=message_to_send.chat.id,
                message_id=message_to_send.message_id,
            )
            sent_successfully += 1
            await sleep(0.5)
        except TelegramError as err:
            failed_to_send += 1
            logger.warning(f"فشل إرسال الرسالة إلى {chat}:\n{err}")
    broadcast_status_message: str = (
        f"اكتمل النشر! أرسلت الرسالة إلى {sent_successfully} مستخدم ومجموعة\n"
    )
    if failed_to_send:
        broadcast_status_message += (
            f" فشل الإرسال إلى {failed_to_send}مستخدمين/مجموعات، غالبا بسبب أن البوت طرد أو أوقف."
        )
    await message.reply_text(
        broadcast_status_message,
        reply_to_message_id=message.message_id,
    )


application.add_handler(
    CommandHandler(
        "broadcast",
        broadcast,  # ty: ignore[invalid-argument-type]
        filters=filters.ChatType.PRIVATE & filters.REPLY & FilterBotAdmin(),
    )
)
