from .. import schemas
from ..models.notes import Note, notes
from datetime import date
from ..database import db
from loguru import logger
from ..static.enums import NoteTypeEnumDB


async def get_notes():
	"""
	Получение всех заметок из БД.
	"""
	query = notes.select()
	return await db.fetch_all(query)


async def create_note(note: schemas.NoteCreate):
	"""
	Создание заметки.
	"""

	completed = False if note.note_type == "task" else None

	query = notes.insert().values(
		note_type=note.note_type,
		text=note.text,
		date=note.date,
		user_id=note.user_id,
		completed=completed
	)
	note_id = await db.execute(query)

	logger.info(f"Note (ID: {note_id}) was successfully created by user with ID: {note.user_id}")

	return {**note.dict(), "id": note_id, "completed": completed}


async def get_user_notes(user: schemas.User, params: schemas.GetNotesParams):
	"""
	Получение списка заметок пользователя.
	По умолчанию делается запрос исходя из дефолтных параметров получения (они в schemas.GetNotesParams).
	Далее проверяются переданные параметры запроса. Если они есть - поэтапно обрабатываются методом
	 Note.handle_get_params.
	"""
	query = notes.select().where(
		(notes.c.date >= date.today()) &
		(notes.c.user_id == user.id)
	).order_by(notes.c.date)  # std sorting/filtering params

	notes_list = await db.fetch_all(query)

	if params != schemas.GetNotesParams():
		notes_list = await Note.handle_get_params(notes_list, params)

	return notes_list


async def update_note(current_note: schemas.Note, updated_note: schemas.NoteUpdate):
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
		case NoteTypeEnumDB.note.value:  # note with type of std note hasn't completing param
			if isinstance(current_params["completed"], bool):
				current_params["completed"] = None
		case NoteTypeEnumDB.task.value:
			if current_params["completed"] is None:
				current_params["completed"] = current_note.completed
	query = notes.update().where(notes.c.id == current_note.id).values(**current_params)
	await db.execute(query)
	return current_params
