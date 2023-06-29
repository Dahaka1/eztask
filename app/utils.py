from datetime import timedelta, datetime
from typing import Any

from jose import jwt

import config
from .database import Base
from .schemas import GetNotesParams
from .static import enums


def verify_password(password, hashed_password) -> bool:
	"""
	Сравнение хешей паролей.
	"""
	return config.pwd_context.verify(password, hashed_password)


def get_password_hash(password) -> str:
	"""
	Хеширование пароля.
	"""
	return config.pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)):
	"""
	Создание JWT-токена. "Живет" в течение переданного времени. По умолчанию время указывается в конфиге.
	В data должен содержаться обязательный для JWT-токена параметр: "sub" (субъект - имя пользователя/email/...).
	"""
	expire = datetime.utcnow() + expires_delta
	data.update({"exp": expire})  # std jwt data param
	encoded_jwt = jwt.encode(claims=data, key=config.JWT_SECRET_KEY, algorithm=config.JWT_SIGN_ALGORITHM)
	return encoded_jwt


def sa_object_to_dict(sa_object: Base) -> dict[str, Any]:
	"""
	Использую AsyncSession из SQLAlchemy.
	Она возвращает из БД не словарь с данными, а объект ORM-модели.
	Для использования, например, с pydantic-схемами, нужна эта функция.
	"""
	obj_dict = sa_object.__dict__
	del obj_dict["_sa_instance_state"]
	return obj_dict


def sa_objects_dicts_list(objects_list: list[Base]) -> list[dict[str, Any]]:
	"""
	Возвращает pydantic-модели (словари) списка SA-объектов.
	"""
	return [sa_object_to_dict(obj) for obj in objects_list]


def convert_query_enums(params_schema: GetNotesParams, params: tuple[Any, ...]) -> GetNotesParams:
	"""
	С типами данных при получении Enum'ов странная путаница.
	Они иногда возвращаются в виде строки, а иногда - в виде Enum'a.
	Поэтому здесь делаю доп. проверку на тип.
	"""
	sorting, period, type_, completed = params

	if sorting is not None:
		params_schema.sorting = sorting.value if isinstance(sorting, enums.NotesOrderByEnum) else sorting
	if period is not None:
		params_schema.period = period.value if isinstance(period, enums.NotesPeriodEnum) else period
	if type_ is not None:
		params_schema.type = type_.value if isinstance(type_, enums.NoteTypeEnum) else type_
	if completed is not None:
		params_schema.completed = completed.value if isinstance(completed, enums.NotesCompletedEnum) else completed

	return params_schema

