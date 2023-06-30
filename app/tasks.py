from . import schemas
from sqlalchemy.ext.asyncio import AsyncSession
from .models.polling import Polling, PollingString
from .static.enums import PollingTypeEnum, NoteTypeEnumDB
import random
from .models.notes import Note
from typing import Optional
from loguru import logger
import sqlalchemy.exc


def get_random_poll_type() -> PollingTypeEnum:
	"""
	Возвращает рандомный тип опроса для пользователя.
	"""
	return random.choice([e.value for e in PollingTypeEnum])


async def initialize_user_polls(user: schemas.User, db: AsyncSession) -> None:
	"""
	Создает опрос для пользователя на текущий день, если его еще нет.
	"""
	if not user.is_staff:
		polls_exists = await Polling.check_today_user_polls(
			user=user, db=db
		)
		if not polls_exists:
			while True:
				random_poll_type = get_random_poll_type()
				poll_string_id = await generate_poll(random_poll_type, user, db)
				if poll_string_id is not None:
					break
			try:
				created_poll = await Polling.create(
					db, poll_type=random_poll_type, polling_string_id=poll_string_id, user_id=user.id
				)
				logger.info(f"Polling ID {created_poll} was successfully generated!")

			except sqlalchemy.exc.IntegrityError:
				# если юзер удалился - не создавать опрос
				pass


async def generate_poll(polling_type: PollingTypeEnum, user: schemas.User, db: AsyncSession) -> Optional[int]:
	"""
	Возвращает ИД случайного опроса (строки) в зависимости от типа опроса.
	Если выпал опрос "note" или "task" - сначала проверяет, есть ли в текущем дне у пользователя задачи/заметки.
	Если их нет - спрашивать не о чем. В таком случае тип опроса переопределяется.
	"""
	match polling_type:
		case PollingTypeEnum.note.value:
			user_notes = await Note.get_user_notes(user=user, db=db)
			if any(user_notes):
				return await PollingString.get_random_poll_text_id(polling_type, db)
			return
		case PollingTypeEnum.task.value:
			user_tasks = await Note.get_user_notes(user=user, db=db, notes_type=NoteTypeEnumDB.task.value)
			if any(user_tasks):
				return await PollingString.get_random_poll_text_id(polling_type, db)
			return
		case _:
			return await PollingString.get_random_poll_text_id(polling_type, db)
