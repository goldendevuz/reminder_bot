from datetime import datetime

import pytz
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from bot.config import TIMEZONE
from bot.handlers.states import AddReminderStates
from bot.models.database import async_session_maker
from bot.models.models import User
from bot.services.reminder_service import ReminderService

router = Router()

DATETIME_FORMAT = "%Y-%m-%d %H:%M"
CANCEL_KB = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="❌ Bekor qilish")]],
    resize_keyboard=True,
    one_time_keyboard=True,
)


@router.message(Command("add"))
async def cmd_add(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(AddReminderStates.waiting_title)
    await message.answer(
        "📦 <b>Yangi eslatma qo'shish</b>\n\n"
        "Buyum nomini kiriting:\n"
        "<i>(Masalan: Sut, Non, Dori)</i>",
        parse_mode="HTML",
        reply_markup=CANCEL_KB,
    )


@router.message(AddReminderStates.waiting_title, F.text == "❌ Bekor qilish")
@router.message(AddReminderStates.waiting_description, F.text == "❌ Bekor qilish")
@router.message(AddReminderStates.waiting_time, F.text == "❌ Bekor qilish")
async def cancel_add(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "❌ Bekor qilindi.",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(AddReminderStates.waiting_title)
async def process_title(message: Message, state: FSMContext) -> None:
    if not message.text or len(message.text.strip()) < 1:
        await message.answer("⚠️ Buyum nomi bo'sh bo'lmasligi kerak. Qaytadan kiriting:")
        return

    if len(message.text.strip()) > 255:
        await message.answer("⚠️ Nom juda uzun (max 255 belgi). Qisqartiring:")
        return

    await state.update_data(title=message.text.strip())
    await state.set_state(AddReminderStates.waiting_description)

    skip_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⏭ O'tkazib yuborish")],
            [KeyboardButton(text="❌ Bekor qilish")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await message.answer(
        "📝 <b>Izoh kiriting</b> (ixtiyoriy):\n"
        "<i>Yoki \"⏭ O'tkazib yuborish\" tugmasini bosing</i>",
        parse_mode="HTML",
        reply_markup=skip_kb,
    )


@router.message(AddReminderStates.waiting_description)
async def process_description(message: Message, state: FSMContext) -> None:
    description = None
    if message.text and message.text.strip() != "⏭ O'tkazib yuborish":
        description = message.text.strip()

    await state.update_data(description=description)
    await state.set_state(AddReminderStates.waiting_time)

    tz = pytz.timezone(TIMEZONE)
    now_str = datetime.now(tz).strftime(DATETIME_FORMAT)

    await message.answer(
        f"⏰ <b>Vaqt kiriting:</b>\n\n"
        f"Format: <code>YYYY-MM-DD HH:MM</code>\n"
        f"Masalan: <code>{now_str}</code>\n\n"
        f"<i>Timezone: {TIMEZONE}</i>",
        parse_mode="HTML",
        reply_markup=CANCEL_KB,
    )


@router.message(AddReminderStates.waiting_time)
async def process_time(message: Message, state: FSMContext, db_user: User) -> None:
    if not message.text:
        await message.answer("⚠️ Vaqtni kiriting:")
        return

    text = message.text.strip()

    # Vaqtni parse qilish
    try:
        remind_at = datetime.strptime(text, DATETIME_FORMAT)
    except ValueError:
        await message.answer(
            f"⚠️ <b>Noto'g'ri format!</b>\n\n"
            f"To'g'ri format: <code>YYYY-MM-DD HH:MM</code>\n"
            f"Masalan: <code>2026-05-01 09:00</code>\n\n"
            f"Qaytadan kiriting:",
            parse_mode="HTML",
        )
        return

    # O'tib ketgan vaqtni tekshirish
    tz = pytz.timezone(TIMEZONE)
    now = datetime.now(tz).replace(tzinfo=None)
    if remind_at <= now:
        await message.answer(
            "⚠️ <b>O'tib ketgan vaqt!</b>\n\n"
            "Kelajakdagi vaqtni kiriting:",
            parse_mode="HTML",
        )
        return

    data = await state.get_data()
    await state.clear()

    async with async_session_maker() as session:
        service = ReminderService(session)
        reminder = await service.create(
            title=data["title"],
            description=data.get("description"),
            remind_at=remind_at,
            created_by_id=db_user.id,
        )

    desc_line = f"\n📝 <b>Izoh:</b> {reminder.description}" if reminder.description else ""
    await message.answer(
        f"✅ <b>Eslatma saqlandi!</b>\n\n"
        f"📦 <b>Buyum:</b> {reminder.title}"
        f"{desc_line}\n"
        f"⏰ <b>Vaqt:</b> {reminder.remind_at.strftime(DATETIME_FORMAT)}\n"
        f"🆔 <b>ID:</b> #{reminder.id}",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove(),
    )
