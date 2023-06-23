import sqlalchemy
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum, Boolean
from ..database import Base
from sqlalchemy.orm import relationship
from ..schemas import GetNotesParams
from ..database import db
from datetime import date
from ..static.enums import NoteTypeEnumDB, NoteTypeEnum, NotesCompletedEnum, NotesOrderByEnum, NotesPeriodEnum


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
	completed = Column(Boolean, nullable=True)  # it's null if note type is std note
	user_id = Column(Integer, ForeignKey("users.id"))

	user = relationship("User", back_populates="notes")

	@staticmethod
	async def handle_get_params(notes_list: list[dict], params: GetNotesParams):
		"""
		Фильтрация и сортировка списка заметок пользователя.

		Если запрошен нестандартный период заметок (не "upcoming" (предстоящие)),
		то делается еще один запрос - загружается полный архив заметок пользователя.
		Сделал так, потому что стандартные запросы на получение предстоящих заметок
		будут производиться практически всегда, реже - просмотр истории всех записей.

		Вся вспомогательная информация по параметрам: см. 'static.enums'
		"""
		if params.period.value != NotesPeriodEnum.upcoming.value:
			notes_list = await db.fetch_all(notes.select().order_by(notes.c.date))

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


# sqlalchemy Table instance for using SA core queries with databases package
notes: sqlalchemy.Table = Note.__table__
