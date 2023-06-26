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


@router.post("/", response_model=schemas.Note, status_code=status.HTTP_201_CREATED)
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
	filtering: Annotated[
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
	if filtering is None:
		filtering = schemas.GetNotesParams()
	return await crud_notes.get_user_notes(current_user, filtering)


@router.get("/{note_id}", response_model=schemas.Note)
async def read_note(
	current_user: Annotated[schemas.User, Depends(get_current_active_user)],
	note: Annotated[schemas.Note, Depends(get_note)]
):
	"""
	Получить данные заметки.
	Доступно только для ее создателя.
	"""
	if note.user_id != current_user.id:
		raise PermissionsError()
	return note


@router.put("/{note_id}", response_model=schemas.Note)
async def update_note(
	current_user: Annotated[schemas.User, Depends(get_current_active_user)],
	current_note: Annotated[schemas.Note, Depends(get_note)],
	note: Annotated[schemas.NoteUpdate, Body(embed=True, title="Updated note")]
):
	"""
	Обновление заметки. Обновить может создатель заметки.
	Нельзя установить дату ранее текущего дня.
	"""
	if current_note.user_id != current_user.id:
		raise PermissionsError()
	if not note.date is None and note.date < date.today():
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
							detail="Date of note should be today or future date.")
	return await crud_notes.update_note(current_note, note)


@router.delete("/{note_id}", response_model=schemas.Note)
async def delete_note(
	current_user: Annotated[schemas.User, Depends(get_current_active_user)],
	current_note: Annotated[schemas.Note, Depends(get_note)]
):
	"""
	Удаление заметки.
	Доступно для создателя заметки.
	"""
	if current_note.user_id != current_user.id:
		raise PermissionsError()
	return await crud_notes.delete_note(current_note)
