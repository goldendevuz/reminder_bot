from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from bot.models.models import User

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, db_user: User, is_new_user: bool) -> None:
    if is_new_user:
        text = (
            f"👋 Xush kelibsiz, <b>{db_user.full_name}</b>!\n\n"
            "Siz oilaviy eslatmalar botiga ro'yxatdan o'tdingiz.\n\n"
            "📋 <b>Buyruqlar:</b>\n"
            "/add — Yangi eslatma qo'shish\n"
            "/list — Barcha eslatmalarni ko'rish\n"
            "/delete — Eslatmani o'chirish\n"
            "/help — Yordam"
        )
    else:
        admin_badge = " 👑" if db_user.is_admin else ""
        text = (
            f"👋 Yana ko'rishganimizdan xursandmiz, <b>{db_user.full_name}</b>{admin_badge}!\n\n"
            "📋 <b>Buyruqlar:</b>\n"
            "/add — Yangi eslatma qo'shish\n"
            "/list — Barcha eslatmalarni ko'rish\n"
            "/delete — Eslatmani o'chirish\n"
            "/help — Yordam"
        )

    await message.answer(text, parse_mode="HTML")


@router.message(Command("obbo"))
async def cmd_help(message: Message) -> None:
    """Noma'lum xabarlar uchun."""
    from aiogram.filters import Command
    # Bu faqat /help uchun yoki noma'lum buyruq uchun
    await message.answer(
        "ℹ️ <b>Mavjud buyruqlar:</b>\n\n"
        "/start — Botni boshlash\n"
        "/add — Yangi eslatma qo'shish\n"
        "/list — Barcha eslatmalarni ko'rish\n"
        "/delete — Eslatmani o'chirish\n"
        "/help — Ushbu yordam xabari",
        parse_mode="HTML",
    )
