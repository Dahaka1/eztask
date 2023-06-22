import sqlalchemy
from sqlalchemy import Column, Integer, String
from ..database import Base
from sqlalchemy.orm import relationship
from databases import Database
from .. import schemas, utils
from typing import Optional


# TODO: после доработки функций с текущими моделями
#  добавить оценку прошедшего дня для пользователя (по разным параметрам)


class User(Base):
	"""
	 Модель пользователя
	TODO: добавить поле ТГ-аккаунта, если буду интегрировать поддержку ТГ
	TODO: добавить поля для аутентификационных данных
	"""
	__tablename__ = "users"

	id = Column(Integer, primary_key=True, index=True)
	email = Column(String(length=50), unique=True, index=True)
	first_name = Column(String(length=50))
	last_name = Column(String(length=50), nullable=True, default=None)
	hashed_password = Column(String)

	notes = relationship("Note", back_populates="user")
	tasks = relationship("Task", back_populates="user")

	@staticmethod
	async def get_user_by_email(db: Database, email: str) -> Optional[schemas.UserInDB]:
		"""
		Поиск пользователя по email.
		"""
		query = users.select().where(users.c.email == email)
		user: dict | None = await db.fetch_one(query)
		if user:
			return schemas.UserInDB(**user)

	@staticmethod
	async def authenticate_user(db: Database, email: str, password: str) -> bool | schemas.UserInDB:
		"""
		Аутентификация пользователя: если пользователя с таким email не существует или
		был введен неправильный пароль - возвращает False; иначе возвращает pydantic-модель пользователя
		с хеш-паролем.
		"""
		user = await User.get_user_by_email(db=db, email=email)
		if not user:
			return False
		if not utils.verify_password(password, user.hashed_password):
			return False
		return user


# sqlalchemy Table instance for using SA core queries with databases package
users: sqlalchemy.Table = User.__table__
