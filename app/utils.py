import config
from datetime import timedelta, datetime
from jose import jwt
from .database import Base
from typing import Any


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
	return [sa_object_to_dict(obj) for obj in objects_list]
