import datetime

from fastapi.security import OAuth2PasswordBearer
from .exceptions import CredentialsException
from fastapi import Depends, status, HTTPException, Path, Query
from typing import Annotated
from jose import JWTError, jwt
import config
from . import schemas
from .models.users import User, users
from .models.notes import notes
from .models.day_ratings import day_ratings
from .database import db

# dependency that expects for token from user
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(
	token: Annotated[str, Depends(oauth2_scheme)]
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
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Disabled user")
	return current_user


async def get_user_id(
	user_id: Annotated[int, Path(ge=1)]
) -> int:
	"""
	Функция проверяет, существует ли пользователь с переданным ИД.
	Возвращает ИД.
	"""
	user_db = await db.fetch_one(
		users.select().where(users.c.id == user_id)
	)
	if user_db is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
	return user_id


async def get_note(
	note_id: Annotated[int, Path(ge=1)]
) -> schemas.Note:
	"""
	Функция проверяет, существует ли заметка с переданным ИД.
	Возвращает pydantic-объект заметки.
	"""
	note = await db.fetch_one(
		notes.select().where(notes.c.id == note_id)
	)
	if note is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
	return note


async def get_day_rating(
	date: Annotated[datetime.date, Query(title="Day rating date", example="2000-01-01")],
	user_id: Annotated[int, Depends(get_user_id)]
):
	"""
	Функция проверяет, существует ли пользователь и его оценка дня по переданной дате.
	"""
	day_rating = await db.fetch_one(
		day_ratings.select().where(
			(day_ratings.c.user_id == user_id) &
			(day_ratings.c.date == date)
		)
	)
	if day_rating is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Day rating not found")
	return day_rating


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
