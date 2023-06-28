from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum, Boolean, DateTime
from ..database import Base
from sqlalchemy.orm import relationship
from ..schemas import GetNotesParams
from datetime import date
from ..static.enums import NoteTypeEnumDB, NoteTypeEnum, NotesCompletedEnum, NotesOrderByEnum, NotesPeriodEnum
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Table
from ..utils import sa_objects_dicts_list


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
	user_id = Column(Integer, ForeignKey("users.id"))

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
		if params.period.value != NotesPeriodEnum.upcoming.value:
			notes_list = await db.execute(select(Note).order_by(notes.c.date))
			notes_list = sa_objects_dicts_list(notes_list.scalars().all())

		match params.period.value:
			case NotesPeriodEnum.past.value:
				notes_list = filter(lambda note: note["date"] < date.today(), notes_list)

		match params.sorting.value:
			case NotesOrderByEnum.date_desc.value:
				notes_list = sorted(notes_list, key=lambda note: note["date"], reverse=True)

		match params.type.value:
			case NoteTypeEnum.note.value:
				notes_list = filter(lambda note: note["note_type"].value == NoteTypeEnum.note.value, notes_list)
			case NoteTypeEnum.task.value:
				notes_list = filter(lambda note: note["note_type"].value == NoteTypeEnum.task.value, notes_list)

				# filter by completing can be applied only when getting notes with type task
				if not params.completed is None:
					match params.completed.value:
						case NotesCompletedEnum.completed.value:
							notes_list = filter(lambda note: note["completed"] is True, notes_list)
						case NotesCompletedEnum.non_completed.value:
							notes_list = filter(lambda note: note["completed"] is False, notes_list)

		return list(notes_list)


# sa table instance for using with db queries
notes: Table = Note.__table__
