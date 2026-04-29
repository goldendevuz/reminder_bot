import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message

from bot.config import BOT_TOKEN
from bot.handlers import add_reminder, delete_reminder, list_reminders, start
from bot.middlewares.access import AccessMiddleware
from bot.models.database import init_db
from bot.scheduler.reminder_scheduler import setup_scheduler

# Logging sozlamalari
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


async def main() -> None:
    logger.info("Bot ishga tushmoqda...")

    # Ma'lumotlar bazasini ishga tushirish
    await init_db()
    logger.info("Ma'lumotlar bazasi tayyor.")

    # Bot va Dispatcher yaratish
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Middleware ulash
    dp.message.middleware(AccessMiddleware())

    # Handlerlarni ro'yxatdan o'tkazish (tartib muhim!)
    dp.include_router(start.router)
    dp.include_router(add_reminder.router)
    dp.include_router(list_reminders.router)
    dp.include_router(delete_reminder.router)

    # /help buyrug'i uchun alohida handler
    @dp.message(Command("help"))
    async def cmd_help(message: Message) -> None:
        await message.answer(
            "ℹ️ <b>Mavjud buyruqlar:</b>\n\n"
            "/start — Botni boshlash\n"
            "/add — Yangi eslatma qo'shish\n"
            "/list — Barcha eslatmalarni ko'rish\n"
            "/delete — Eslatmani o'chirish\n"
            "/cancel — Joriy amalni bekor qilish\n"
            "/help — Ushbu yordam xabari\n\n"
            "<b>Eslatma formati:</b>\n"
            "<code>YYYY-MM-DD HH:MM</code>\n"
            "Masalan: <code>2026-05-01 09:00</code>",
        )

    # Schedulerni ishga tushirish
    scheduler = setup_scheduler(bot)
    scheduler.start()
    logger.info("Scheduler ishga tushdi (har 60 soniyada tekshiradi).")

    # Botni ishga tushirish
    try:
        logger.info("Bot polling boshlandi. To'xtatish uchun Ctrl+C bosing.")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        scheduler.shutdown()
        await bot.session.close()
        logger.info("Bot to'xtatildi.")


if __name__ == "__main__":
    asyncio.run(main())
