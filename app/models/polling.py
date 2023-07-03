from ..database import Base
from sqlalchemy import Column, Integer, Boolean, DateTime, Enum, ForeignKey, select, Date, String
from ..static.enums import PollingTypeEnum
from sqlalchemy.sql import func
from .. import schemas
from sqlalchemy.ext.asyncio import AsyncSession
import datetime
import random
from typing import Any
from ..utils import sa_objects_dicts_list


polling_type_enum = Enum(
	PollingTypeEnum,
	name="celery_task_enum",
	create_constraint=True,
	validate_strings=True
)  # enum type for DB


class Polling(Base):
	"""
	Таблица для создания и хранения опросов для пользователя.

	Формируются посредством BackgroundTasks (fastapi).

	Делать pydantic-форму не стал - не необходимо, избыточно.
	"""
	__tablename__ = "polling"

	id = Column(Integer, primary_key=True, index=True)
	created_at = Column(Date, server_default=func.current_date())
	poll_type = Column(polling_type_enum)
	polling_string_id = Column(Integer, ForeignKey("polling_strings.id", onupdate="CASCADE", ondelete="RESTRICT"))
	user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"))
	completed = Column(Boolean, default=False)
	completed_at = Column(DateTime(timezone=True), nullable=True, default=None, onupdate=func.now())

	@staticmethod
	async def check_today_user_polls(user: schemas.User, db: AsyncSession) -> bool:
		"""
		Проверяет, сформирован ли уже опрос на текущий день для пользователя.
		"""
		query = select(Polling).where(
			(Polling.user_id == user.id) &
			(Polling.created_at == datetime.date.today())
		)
		result = await db.execute(query)

		today_polls = result.scalars().all()

		if not any(today_polls):
			return False
		return True


class PollingString(Base):
	"""
	Набор вопросов для пользователя в зависимости от типа опроса.
	"""
	__tablename__ = "polling_strings"

	id = Column(Integer, primary_key=True, index=True)
	poll_type = Column(polling_type_enum)
	text = Column(String)

	@staticmethod
	async def get_random_poll_text_id(polling_type: PollingTypeEnum, db: AsyncSession) -> int:
		"""
		Возвращает случайный опрос по указанному типу опроса.
		"""
		query = select(PollingString).where(
			PollingString.poll_type == polling_type
		)
		result = await db.execute(query)
		strings = result.scalars().all()

		return random.choice(strings).id

	@staticmethod
	async def get_polling_type_strings(polling_type: PollingTypeEnum, db: AsyncSession) -> list[dict[str, Any]]:
		"""
		Возвращает все возможные опросы с указанным типом.
		"""
		query = select(PollingString).where(
			PollingString.poll_type == polling_type
		)
		result = await db.execute(query)
		strings = result.scalars().all()

		if any(strings):
			return sa_objects_dicts_list(strings)
