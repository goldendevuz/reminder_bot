from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from bot.handlers.states import DeleteReminderStates
from bot.models.database import async_session_maker
from bot.models.models import User
from bot.services.reminder_service import ReminderService

router = Router()

DATETIME_FORMAT = "%Y-%m-%d %H:%M"


@router.message(Command("delete"))
async def cmd_delete(message: Message, state: FSMContext) -> None:
    # Avval eslatmalar ro'yxatini ko'rsatamiz
    async with async_session_maker() as session:
        service = ReminderService(session)
        reminders = await service.get_upcoming()

    if not reminders:
        await message.answer(
            "📭 O'chirish uchun eslatmalar yo'q.",
            parse_mode="HTML",
        )
        return

    lines = ["📋 <b>Eslatmalar (o'chirish uchun ID kiriting):</b>\n"]
    for r in reminders:
        desc = f" — {r.description}" if r.description else ""
        creator_name = r.creator.full_name if r.creator else "Noma'lum"
        lines.append(
            f"🆔 <b>#{r.id}</b> | {r.title}{desc}\n"
            f"   ⏰ {r.remind_at.strftime(DATETIME_FORMAT)}"
            f" | 👤 {creator_name}"
        )

    lines.append("\n<i>O'chirish uchun eslatma ID raqamini yuboring yoki /cancel bilan bekor qiling.</i>")

    await state.set_state(DeleteReminderStates.waiting_id)
    await message.answer("\n".join(lines), parse_mode="HTML")


@router.message(DeleteReminderStates.waiting_id, F.text == "/cancel")
async def cancel_delete(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("❌ Bekor qilindi.", reply_markup=ReplyKeyboardRemove())


@router.message(DeleteReminderStates.waiting_id)
async def process_delete_id(message: Message, state: FSMContext, db_user: User) -> None:
    if not message.text or not message.text.strip().lstrip("#").isdigit():
        await message.answer(
            "⚠️ Faqat raqam kiriting. Masalan: <code>5</code> yoki <code>#5</code>",
            parse_mode="HTML",
        )
        return

    reminder_id = int(message.text.strip().lstrip("#"))

    async with async_session_maker() as session:
        service = ReminderService(session)
        reminder = await service.get_by_id(reminder_id)

        if not reminder:
            await message.answer(f"⚠️ #{reminder_id} ID li eslatma topilmadi.")
            return

        if reminder.is_sent:
            await message.answer("⚠️ Bu eslatma allaqachon yuborilgan, o'chirib bo'lmaydi.")
            await state.clear()
            return

        can_delete = await service.can_delete(reminder, db_user.telegram_id)
        if not can_delete:
            await message.answer(
                "⛔ Siz bu eslatmani o'chira olmaysiz.\n"
                "Faqat eslatmani yaratgan kishi yoki admin o'chira oladi."
            )
            await state.clear()
            return

        title = reminder.title
        await service.delete(reminder_id)

    await state.clear()
    await message.answer(
        f"✅ <b>#{reminder_id} — \"{title}\"</b> eslatmasi o'chirildi.",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove(),
    )
