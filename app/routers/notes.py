from fastapi import APIRouter, Depends, Body, HTTPException, status
from .. import schemas
from ..dependencies import get_current_active_user, get_note
from typing import Annotated
from ..crud import crud_notes
from datetime import date
from ..exceptions import PermissionsError


router = APIRouter(
	prefix="/notes",
	tags=["notes"]
)

# TODO: note delete


@router.get("/", response_model=list[schemas.Note])
async def read_notes(
	current_user: Annotated[schemas.User, Depends(get_current_active_user)]
):
	"""
	Получение списка всех заметок.
	Доступно только для is_staff пользователей.
	"""
	if current_user.is_staff:
		return await crud_notes.get_notes()
	raise PermissionsError()


@router.post("/", response_model=schemas.Note)
async def create_note(
	current_user: Annotated[schemas.User, Depends(get_current_active_user)],
	note: Annotated[schemas.NoteCreate, Body(embed=True, title="Note creating params")]
):
	"""
	Создание пользователем заметки.
	По умолчанию тип - "заметка". Опциональный тип - "задача". "Задача" может быть завершена, в отличие от заметки.
	Если не указана дата заметки, то по умолчанию устанавливается сегодняшний день.
	Is_staff-пользователи могут создавать заметки с любой датой, включая прошедшие (для теста и т.д.).
	"""
	note.user_id = current_user.id

	if not current_user.is_staff and note.date is not None and note.date < date.today():
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
							detail="Date of note should be today or future date.")
	return await crud_notes.create_note(note)


@router.get("/me", response_model=list[schemas.Note])
async def read_notes_me(
	current_user: Annotated[schemas.User, Depends(get_current_active_user)],
	params: Annotated[
		schemas.GetNotesParams | None,
		Body(embed=True, title="Sorting and filtering notes params")
	] = None
):
	"""
	Метод возвращает все заметки пользователя.
	Возможна дополнительная сортировка/фильтрация.
	По умолчанию возвращаются только сегодняшние/предстоящие заметки
	 всех типов с сортировкой по дате создания.
	"""
	if params is None:
		params = schemas.GetNotesParams()
	return await crud_notes.get_user_notes(current_user, params)


@router.get("/{note_id}", response_model=schemas.Note)
async def read_note(
	current_user: Annotated[schemas.User, Depends(get_current_active_user)],
	note: Annotated[schemas.Note, Depends(get_note)]
):
	"""
	Получить данные заметки.
	Доступно только для ее создателя или для is_staff-пользователя.
	"""
	if not current_user.is_staff and note.user_id != current_user.id:
		raise PermissionsError()
	return note


@router.put("/{note_id}", response_model=schemas.Note)
async def update_note(
	current_user: Annotated[schemas.User, Depends(get_current_active_user)],
	current_note: Annotated[schemas.Note, Depends(get_note)],
	note: Annotated[schemas.NoteUpdate, Body(embed=True)]  # updated note data
):
	"""
	Обновление заметки. Обновить может is_staff-пользователь или создатель заметки.
	Нельзя установить дату ранее текущего дня.
	"""
	if not current_user.is_staff and current_note.user_id != current_user.id:
		raise PermissionsError()
	if not note.date is None and note.date < date.today():
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
							detail="Date of note should be today or future date.")
	return await crud_notes.update_note(current_note, note)
