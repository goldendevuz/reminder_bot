import logging

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.models.database import async_session_maker
from bot.services.reminder_service import ReminderService
from bot.services.user_service import UserService

logger = logging.getLogger(__name__)

DATETIME_FORMAT = "%Y-%m-%d %H:%M"


async def check_and_send_reminders(bot: Bot) -> None:
    """
    Har 1 minutda ishga tushadi.
    Vaqti kelgan eslatmalarni barcha faol userlarga yuboradi.
    """
    async with async_session_maker() as session:
        reminder_service = ReminderService(session)
        user_service = UserService(session)

        pending = await reminder_service.get_pending_to_send()
        if not pending:
            return

        users = await user_service.get_all_active()
        if not users:
            logger.warning("Faol foydalanuvchilar yo'q, eslatmalar yuborilmadi.")
            return

        for reminder in pending:
            creator_name = reminder.creator.full_name if reminder.creator else "Noma'lum"
            desc_line = f"\n📝 <b>Izoh:</b> {reminder.description}" if reminder.description else ""
            text = (
                f"🔔 <b>Eslatma!</b>\n\n"
                f"📦 <b>Buyum:</b> {reminder.title}"
                f"{desc_line}\n"
                f"⏰ <b>Vaqt:</b> {reminder.remind_at.strftime(DATETIME_FORMAT)}\n"
                f"👤 <b>Qo'shgan:</b> {creator_name}"
            )

            sent_count = 0
            failed_count = 0

            for user in users:
                try:
                    await bot.send_message(
                        chat_id=user.telegram_id,
                        text=text,
                        parse_mode="HTML",
                    )
                    sent_count += 1
                except Exception as e:
                    failed_count += 1
                    logger.warning(
                        f"Foydalanuvchi {user.telegram_id} ga yuborib bo'lmadi: {e}"
                    )

            await reminder_service.mark_as_sent(reminder.id)
            logger.info(
                f"Eslatma #{reminder.id} '{reminder.title}': "
                f"{sent_count} ta yuborildi, {failed_count} ta muvaffaqiyatsiz."
            )


def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    """Schedulerni yaratadi va ishga tushiradi."""
    scheduler = AsyncIOScheduler(timezone="Asia/Tashkent")
    scheduler.add_job(
        check_and_send_reminders,
        trigger="interval",
        seconds=60,
        kwargs={"bot": bot},
        id="reminder_checker",
        replace_existing=True,
        max_instances=1,
    )
    return scheduler
