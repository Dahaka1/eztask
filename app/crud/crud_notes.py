from .. import schemas
from ..models.notes import Note, notes
from datetime import date
from loguru import logger
from ..static.enums import NoteTypeEnumDB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete
from .. utils import sa_objects_dicts_list, convert_query_enums


async def get_notes(db: AsyncSession):
	"""
	Получение всех заметок из БД.
	"""
	query = select(Note).order_by(notes.c.created_at)
	result = await db.execute(query)
	return sa_objects_dicts_list(result.scalars().all())


async def create_note(note: schemas.NoteCreate, db: AsyncSession):
	"""
	Создание заметки.
	"""

	# Тут я искренне не понимаю, в чем проблема: иногда переданный note_type - это строка,
	# а иногда - поле enum'а. Хоть и всегда должен быть полем NoteTypeEnum'а, как определено в pydantic-схеме.
	# Поэтому делаю доп. проверку.
	note_type = note.note_type.value if isinstance(note.note_type, NoteTypeEnumDB) else note.note_type

	completed = False if note_type == NoteTypeEnumDB.task.value else None

	query = insert(Note).values(
		note_type=note.note_type,
		text=note.text,
		date=note.date,
		user_id=note.user_id,
		completed=completed,
		created_at=note.created_at
	)
	note_id = await db.execute(query)
	note_id = note_id.inserted_primary_key[0]
	await db.commit()

	logger.info(f"Note (ID: {note_id}) was successfully created by user with ID: {note.user_id}")

	return {**note.dict(), "id": note_id, "completed": completed}


async def get_user_notes(user: schemas.User, filtering_params: tuple, db: AsyncSession):
	"""
	Получение списка заметок пользователя.
	По умолчанию делается запрос исходя из дефолтных параметров получения (они в schemas.GetNotesParams).
	Далее проверяются переданные параметры запроса. Если они есть - поэтапно обрабатываются методом
	 Note.handle_get_params.
	"""
	default_params = convert_query_enums(
		params_schema=schemas.GetNotesParams(), params=filtering_params
	)

	query = select(Note).where(
		(notes.c.date >= date.today()) &
		(notes.c.user_id == user.id)
	).order_by(notes.c.date)  # std sorting/filtering params

	result = await db.execute(query)
	notes_list = sa_objects_dicts_list(result.scalars().all())

	if default_params != schemas.GetNotesParams():
		notes_list = await Note.handle_get_params(notes_list, default_params, db=db)

	return notes_list


async def update_note(current_note: schemas.Note, updated_note: schemas.NoteUpdate, db: AsyncSession):
	"""
	Обновление параметров текущей заметки согласно новым переданным.
	Предусмотрено определение параметра "completed" относительно типа заметки:
	 если заметка - не задача, то "completed" может быть только со значением None, а не True/False,
	 и наоборот.
	"""
	updated_params = dict(updated_note)
	current_params = dict(current_note)
	for param, val in updated_params.items():
		if not val is None:
			current_params[param] = val
	match current_params["note_type"].value:
		case NoteTypeEnumDB.note.value:  # note with type of std note (not task) hasn't completing param
			if isinstance(current_params["completed"], bool):
				current_params["completed"] = None
		case NoteTypeEnumDB.task.value:
			if current_params["completed"] is None:
				current_params["completed"] = current_note.completed or False
	query = update(Note).where(notes.c.id == current_note.id).values(**current_params)
	await db.execute(query)
	await db.commit()

	logger.info(f"Note ID: {current_note.id} was successfully updated by creator (ID: {current_note.user_id})")

	return current_params


async def delete_note(current_note: schemas.Note, db: AsyncSession):
	"""
	Удаление заметки. Возвращает pydantic-объект удаленной заметки.
	"""
	query = delete(Note).where(notes.c.id == current_note.id)
	await db.execute(query)
	await db.commit()

	logger.info(f"Note ID: {current_note.id} was successfully deleted by creator (ID: {current_note.user_id})")

	return current_note
