import datetime
from datetime import date
from typing import Any

from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum, Boolean, DateTime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import Base
from ..schemas import GetNotesParams
from ..static.enums import NoteTypeEnumDB, NoteTypeEnum, NotesCompletedEnum, NotesOrderByEnum, NotesPeriodEnum
from ..utils import sa_objects_dicts_list
from .. import schemas

note_type_enum = Enum(
	NoteTypeEnumDB,
	name="note_type_enum",
	create_constraint=True,
	validate_strings=True
)  # enum type for DB


class Note(Base):
	"""
	Модель заметки.
	"""
	__tablename__ = "notes"

	id = Column(Integer, primary_key=True, index=True)
	note_type = Column(note_type_enum)
	text = Column(String(length=1000))
	date = Column(Date)
	created_at = Column(DateTime(timezone=True))
	completed = Column(Boolean, nullable=True)  # it's null if note type is std note
	user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"))

	@staticmethod
	async def handle_get_params(notes_list: list[dict], params: GetNotesParams, db: AsyncSession):
		"""
		Фильтрация и сортировка списка заметок пользователя.

		Если запрошен нестандартный период заметок (не "upcoming" (предстоящие)),
		то делается еще один запрос - загружается полный архив заметок пользователя.
		Сделал так, потому что стандартные запросы на получение предстоящих заметок
		будут производиться практически всегда, реже - просмотр истории всех записей.

		Вся вспомогательная информация по параметрам: см. 'static.enums'
		"""
		if params.period != NotesPeriodEnum.upcoming.value:
			notes_list = await db.execute(select(Note).order_by(Note.date))
			notes_list = sa_objects_dicts_list(
				list(notes_list.scalars().all())
			)

		match params.period:
			case NotesPeriodEnum.past.value:
				notes_list = filter(lambda note: note["date"] < date.today(), notes_list)

		match params.sorting:
			case NotesOrderByEnum.date_desc.value:
				notes_list = sorted(notes_list, key=lambda note: note["date"], reverse=True)

		match params.type:
			case NoteTypeEnum.note.value:
				notes_list = filter(lambda note: note["note_type"].value == NoteTypeEnum.note.value, notes_list)
			case NoteTypeEnum.task.value:
				notes_list = filter(lambda note: note["note_type"].value == NoteTypeEnum.task.value, notes_list)

				# filter by completing can be applied only when getting notes with type task
				if not params.completed is None:
					match params.completed:
						case NotesCompletedEnum.completed.value:
							notes_list = filter(lambda note: note["completed"] is True, notes_list)
						case NotesCompletedEnum.non_completed.value:
							notes_list = filter(lambda note: note["completed"] is False, notes_list)

		return list(notes_list)

	@staticmethod
	async def get_user_notes(user: schemas.User,
							 db: AsyncSession,
							 notes_date: datetime = None,
							 notes_type: str = NoteTypeEnumDB.note.value) -> \
		list[dict[str, Any]]:
		"""
		Возвращает все заметки пользователя напрямую из БД.
		По умолчанию с датой текущего дня и типом "note".

		Пишу здесь аналогичную CRUD 'get_user_notes' функцию, ибо здесь
		 делаю другой sql-запрос, получаю заметки только по одному дню - экономия ресурсов.
		"""
		if notes_type not in [note_type.value for note_type in NoteTypeEnumDB]:
			raise AttributeError
		if notes_date is None:
			notes_date = datetime.date.today()
		query = select(Note).where(
			(Note.user_id == user.id) &
			(Note.date == notes_date) &
			(Note.note_type == notes_type)
		)
		result = await db.execute(query)

		notes = list(result.scalars().all())

		return sa_objects_dicts_list(notes)
