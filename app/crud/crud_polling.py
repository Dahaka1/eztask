from ..models.polling import Polling, PollingString
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update
from ..static.enums import PollingTypeEnum
import datetime
from typing import Optional, Any
from ..utils import sa_object_to_dict
from ..static.strings import polling_strings
from loguru import logger


async def create_polling(db: AsyncSession, **kwargs) -> int:
	"""
	Создание опроса. Ссылается на вопрос (строку).
	"""
	query = insert(Polling).values(
		**kwargs
	)
	inserted_poll = await db.execute(query)
	await db.commit()

	return inserted_poll.inserted_primary_key[0]


async def get_user_polling(user_id: int, db: AsyncSession, date: datetime.date = None) -> Optional[dict[str, Any]]:
	"""
	Поиск опроса для пользователя по дате.
	"""
	if date is None:
		date = datetime.date.today()
	query = select(Polling).where(
		(Polling.user_id == user_id) &
		(Polling.created_at == date)
	)
	result = await db.execute(query)
	polling = result.scalar()
	if polling:
		return sa_object_to_dict(polling)


async def update_user_polling(polling_id: int, db: AsyncSession) -> None:
	"""
	Обновление статуса опроса.
	"""
	query = update(Polling).where(
		Polling.id == polling_id
	).values(completed=True)
	await db.execute(query)
	await db.commit()


async def create_polling_string(text: str, polling_type: PollingTypeEnum, db: AsyncSession) -> None:
	"""
	Добавление опросов в базу (вопросов для рандомного выбора).
	"""
	query = insert(PollingString).values(
		poll_type=polling_type,
		text=text
	)
	await db.execute(query)
	await db.commit()


async def create_polling_strings(db: AsyncSession):
	"""
	Создание опросов по умолчанию при запуске сервера, если их еще нет.
	"""
	strings_existing_query = select(PollingString)
	existing_strings_result = await db.execute(strings_existing_query)
	existing_strings = existing_strings_result.scalars().all()
	if not any(existing_strings):
		for poll_type in polling_strings:
			strings = polling_strings.get(poll_type)
			for s in strings:
				await create_polling_string(text=s, polling_type=poll_type, db=db)
		logger.info(f"Default 'Polling_Strings' relation data was successfully created")
