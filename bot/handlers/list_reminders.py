from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.models.database import async_session_maker
from bot.services.reminder_service import ReminderService

router = Router()

DATETIME_FORMAT = "%Y-%m-%d %H:%M"


@router.message(Command("list"))
async def cmd_list(message: Message) -> None:
    async with async_session_maker() as session:
        service = ReminderService(session)
        reminders = await service.get_upcoming()

    if not reminders:
        await message.answer(
            "📭 <b>Hozircha eslatmalar yo'q.</b>\n\n"
            "Yangi eslatma qo'shish uchun /add buyrug'ini ishlating.",
            parse_mode="HTML",
        )
        return

    lines = ["📋 <b>Kelajakdagi eslatmalar:</b>\n"]
    for idx, r in enumerate(reminders, start=1):
        desc = f" — {r.description}" if r.description else ""
        creator_name = r.creator.full_name if r.creator else "Noma'lum"
        lines.append(
            f"{idx}. <b>{r.title}</b>{desc}\n"
            f"   ⏰ {r.remind_at.strftime(DATETIME_FORMAT)}"
            f" | 👤 {creator_name}"
            f" | 🆔 #{r.id}"
        )

    await message.answer("\n".join(lines), parse_mode="HTML")
