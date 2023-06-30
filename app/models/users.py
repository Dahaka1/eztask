from typing import Optional, Any

from sqlalchemy import Column, Integer, String, Boolean, DateTime, select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import schemas, utils
from ..database import Base
from ..utils import sa_object_to_dict


# TODO: после доработки функций с текущими моделями
#  добавить оценку прошедшего дня для пользователя (по разным параметрам)


class User(Base):
	"""
	 Модель пользователя
	TODO: добавить поле ТГ-аккаунта, если буду интегрировать поддержку ТГ
	"""
	__tablename__ = "users"

	id = Column(Integer, primary_key=True, index=True)
	email = Column(String(length=50), unique=True, index=True)
	first_name = Column(String(length=50))
	last_name = Column(String(length=50), nullable=True, default=None)
	is_staff = Column(Boolean, default=False)
	disabled = Column(Boolean, default=False)
	hashed_password = Column(String)
	registered_at = Column(DateTime(timezone=True))

	@staticmethod
	async def get_user_by_email(db: AsyncSession, email: str) -> Optional[schemas.UserInDB]:
		"""
		Поиск пользователя по email.
		"""
		query = select(User).where(User.email == email)
		result = await db.execute(query)
		user: User | None = result.scalar()
		if isinstance(user, User):
			user_dict: dict[str, Any] = sa_object_to_dict(user)
			return schemas.UserInDB(**user_dict)

	@staticmethod
	async def authenticate_user(db: AsyncSession, email: str, password: str) -> None | schemas.UserInDB:
		"""
		Аутентификация пользователя: если пользователя с таким email не существует или
		был введен неправильный пароль - возвращает False; иначе возвращает pydantic-модель пользователя
		с хеш-паролем.
		"""
		user = await User.get_user_by_email(db=db, email=email)
		if not user:
			return
		if not utils.verify_password(password, user.hashed_password):
			return
		return user

	@staticmethod
	def check_user_permissions(current_user: schemas.User, user_id: int) -> bool:
		"""
		:param current_user: Пользователь, совершающий CRUD-действие.
		:param user_id: ИД пользователя, над данными которого совершается операция.
		:return: Возвращает True, если проверка прошла успешно.

		Действие (удаление/обновление/...) над данными пользователя возможно только для:
		- Самого пользователя;
		- Стафф-пользователя (is_staff=True в БД).

		Действие над данными заметки возможно только для:
		- Создателя заметки.
		"""
		if not current_user.is_staff and current_user.id != user_id:
			return False
		return True
