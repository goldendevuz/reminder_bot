from datetime import datetime

import pytz
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bot.config import TIMEZONE
from bot.models.models import Reminder, User


class ReminderService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.tz = pytz.timezone(TIMEZONE)

    def now_local(self) -> datetime:
        """Hozirgi vaqt (Asia/Tashkent)."""
        return datetime.now(self.tz).replace(tzinfo=None)

    async def create(
        self,
        title: str,
        remind_at: datetime,
        created_by_id: int,
        description: str | None = None,
    ) -> Reminder:
        reminder = Reminder(
            title=title,
            description=description,
            remind_at=remind_at,
            created_by=created_by_id,
            is_sent=False,
        )
        self.session.add(reminder)
        await self.session.commit()
        await self.session.refresh(reminder)
        return reminder

    async def get_upcoming(self) -> list[Reminder]:
        """Hali yuborilmagan, kelajakdagi barcha eslatmalar."""
        now = self.now_local()
        result = await self.session.execute(
            select(Reminder)
            .options(selectinload(Reminder.creator))
            .where(Reminder.is_sent == False, Reminder.remind_at > now)  # noqa: E712
            .order_by(Reminder.remind_at.asc())
        )
        return list(result.scalars().all())

    async def get_pending_to_send(self) -> list[Reminder]:
        """Vaqti kelgan, yuborilmagan eslatmalar (scheduler uchun)."""
        now = self.now_local()
        result = await self.session.execute(
            select(Reminder)
            .options(selectinload(Reminder.creator))
            .where(Reminder.is_sent == False, Reminder.remind_at <= now)  # noqa: E712
        )
        return list(result.scalars().all())

    async def mark_as_sent(self, reminder_id: int) -> None:
        await self.session.execute(
            update(Reminder)
            .where(Reminder.id == reminder_id)
            .values(is_sent=True)
        )
        await self.session.commit()

    async def get_by_id(self, reminder_id: int) -> Reminder | None:
        result = await self.session.execute(
            select(Reminder)
            .options(selectinload(Reminder.creator))
            .where(Reminder.id == reminder_id)
        )
        return result.scalar_one_or_none()

    async def delete(self, reminder_id: int) -> bool:
        reminder = await self.get_by_id(reminder_id)
        if not reminder:
            return False
        await self.session.delete(reminder)
        await self.session.commit()
        return True

    async def can_delete(self, reminder: Reminder, telegram_id: int) -> bool:
        """Faqat egasi yoki admin o'chira oladi."""
        user_result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            return False
        return reminder.created_by == user.id or user.is_admin
