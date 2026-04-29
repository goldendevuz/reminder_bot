from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models.models import User


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def get_or_create(
        self,
        telegram_id: int,
        full_name: str,
        username: str | None = None,
        is_admin: bool = False,
    ) -> tuple[User, bool]:
        """
        Foydalanuvchini qaytaradi yoki yangi yaratadi.
        Returns: (user, created)
        """
        user = await self.get_by_telegram_id(telegram_id)
        if user:
            # Ma'lumotlarni yangilash
            user.full_name = full_name
            user.username = username
            await self.session.commit()
            return user, False

        user = User(
            telegram_id=telegram_id,
            full_name=full_name,
            username=username,
            is_active=True,
            is_admin=is_admin,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user, True

    async def get_all_active(self) -> list[User]:
        result = await self.session.execute(
            select(User).where(User.is_active == True)  # noqa: E712
        )
        return list(result.scalars().all())

    async def set_active(self, telegram_id: int, is_active: bool) -> None:
        await self.session.execute(
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(is_active=is_active)
        )
        await self.session.commit()

    async def count_active(self) -> int:
        from sqlalchemy import func, select
        result = await self.session.execute(
            select(func.count()).select_from(User).where(User.is_active == True)  # noqa: E712
        )
        return result.scalar_one()
