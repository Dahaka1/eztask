import datetime
from typing import Annotated
from typing import AsyncGenerator

from fastapi import Depends, status, HTTPException, Path, Query
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import config
from . import schemas
from .database import async_session_maker
from .exceptions import CredentialsException
from .models.day_ratings import DayRating
from .models.notes import Note
from .models.users import User
from .utils import sa_object_to_dict

# dependency that expects for token from user
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
	async with async_session_maker() as session:
		yield session


async def get_current_user(
	token: Annotated[str, Depends(oauth2_scheme)],
	db: Annotated[AsyncSession, Depends(get_async_session)]
) -> schemas.UserInDB:
	"""
	Функция для декодирования получаемого от пользователя токена.
	Если токен не содержит email или не поддается декодированию, поднимается ошибка авторизации.
	Если токен корректный, но нет пользователя с указанным email - тоже.
	Эта функция в dependency, потому что будет по дефолту срабатывать при каждом запросе от пользователей.
	"""
	try:
		payload = jwt.decode(token=token, key=config.JWT_SECRET_KEY, algorithms=[config.JWT_SIGN_ALGORITHM])
		email: str | None = payload.get("sub")  # sub is std jwt token data param
		if email is None:
			raise CredentialsException()
		token_data = schemas.TokenData(email=email)
	except JWTError:
		raise CredentialsException()
	user = await User.get_user_by_email(db=db, email=token_data.email)
	if user is None:
		raise CredentialsException()
	return user


async def get_current_active_user(
	current_user: Annotated[schemas.User, Depends(get_current_user)]
) -> schemas.User:
	"""
	Функция проверяет, заблокирован ли пользователь, сделавший запрос.
	"""
	if current_user.disabled:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Disabled user")
	return current_user


async def get_user_id(
	user_id: Annotated[int, Path(ge=1)],
	db: Annotated[AsyncSession, Depends(get_async_session)]
) -> int:
	"""
	Функция проверяет, существует ли пользователь с переданным ИД.
	Возвращает ИД.
	"""
	result = await db.execute(
		select(User).where(User.id == user_id)
	)
	user_db = result.scalar()
	if user_db is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
	return user_id


async def get_note(
	note_id: Annotated[int, Path(ge=1)],
	db: Annotated[AsyncSession, Depends(get_async_session)]
) -> schemas.Note:
	"""
	Функция проверяет, существует ли заметка с переданным ИД.
	Возвращает pydantic-объект заметки.
	"""
	result = await db.execute(
		select(Note).where(Note.id == note_id)
	)
	note = result.scalar()
	if note is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
	note_dict = sa_object_to_dict(note)

	return schemas.Note(**note_dict)


async def get_day_rating(
	date: Annotated[datetime.date, Query(title="Day rating date", example="2000-01-01")],
	user_id: Annotated[int, Depends(get_user_id)],
	db: Annotated[AsyncSession, Depends(get_async_session)]
):
	"""
	Функция проверяет, существует ли пользователь и его оценка дня по переданной дате.
	"""
	result = await db.execute(
		select(DayRating).where(
			(DayRating.user_id == user_id) &
			(DayRating.date == date)
		)
	)
	day_rating = result.scalar()
	if day_rating is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Day rating not found")
	day_rating = sa_object_to_dict(day_rating)

	return schemas.DayRating(**day_rating)


async def get_day_rating_filters(
	mood: Annotated[bool, Query()] = False,
	notes: Annotated[bool, Query()] = False,
	next_day_expectations: Annotated[bool, Query()] = False,
	health: Annotated[bool, Query()] = False
):
	"""
	Получение параметров фильтрации оценок дня из параметров запроса.
	"""
	return {
		"mood": mood,
		"notes": notes,
		"health": health,
		"next_day_expectations": next_day_expectations
	}
