from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from bot.config import ADMIN_IDS
from bot.models.database import async_session_maker
from bot.services.user_service import UserService


class AccessMiddleware(BaseMiddleware):
    """
    Har bir xabarda foydalanuvchi mavjudligini tekshiradi.
    Yangi admin ID-larini avtomatik qo'shadi.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message) or not event.from_user:
            return await handler(event, data)

        tg_user = event.from_user
        is_admin = tg_user.id in ADMIN_IDS

        async with async_session_maker() as session:
            user_service = UserService(session)
            user, created = await user_service.get_or_create(
                telegram_id=tg_user.id,
                full_name=tg_user.full_name,
                username=tg_user.username,
                is_admin=is_admin,
            )

            if not user.is_active:
                await event.answer(
                    "⛔ Sizga botdan foydalanish ruxsat etilmagan.\n"
                    "Admin bilan bog'laning."
                )
                return

            data["db_user"] = user
            data["db_session"] = session
            data["is_new_user"] = created

        return await handler(event, data)
