from loguru import logger
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from .. import schemas
from ..models.users import User, users
from ..utils import get_password_hash
from ..utils import sa_objects_dicts_list, sa_object_to_dict


async def get_users(db: AsyncSession):
	"""
	:return: Возвращает список всех пользователей (pydantic-модели)
	"""
	query = select(User).order_by(users.c.registered_at)
	result = await db.execute(query)
	return sa_objects_dicts_list(result.scalars().all())


async def create_user(user: schemas.UserCreate, db: AsyncSession):
	"""
	:return: Возвращает словарь с данными созданного юзера.
	"""
	hashed_password = get_password_hash(user.password)
	query = insert(User).values(
		email=user.email,
		first_name=user.first_name,
		last_name=user.last_name,
		hashed_password=hashed_password,
		is_staff=False,
		disabled=False,
		registered_at=user.registered_at
	)  # пришлось тут определить is_staff и disabled опять - почему-то дефолтные значения в
	# models.users.User не срабатывают :(
	user_id = await db.execute(query)
	await db.commit()

	user_id = user_id.inserted_primary_key[0]

	logger.info(f"User {user.email} (ID: {user_id}) was successfully registered")

	return {
		**user.dict(), "id": user_id
	}


async def update_user(user: schemas.UserUpdate, user_id: int, action_by: schemas.User, db: AsyncSession):
	"""
	:return: Возвращает словарь с данными обновленного пользователя.
	"""
	query = select(User).where(users.c.id == user_id)
	result = await db.execute(query)
	user_db = sa_object_to_dict(result.scalar())
	for key, val in user.dict().items():
		if not val is None:
			if key == "password":
				if action_by.id != user_id:
					pass  # only user can set a new password, not staff
				else:
					hashed_password = get_password_hash(val)
					user_db["hashed_password"] = hashed_password
			else:
				user_db[key] = val
	query = update(User).where(users.c.id == user_id).values(**user_db)
	await db.execute(query)
	await db.commit()

	logger.info(f"User {user_db['email']} (ID: {user_id}) was successfully updated by user "
				f"{action_by.email} with ID {action_by.id}")

	return user_db


async def delete_user(user_id: int, action_by: schemas.User, db: AsyncSession) -> dict[str, int]:
	"""
	:return: Возвращает ИД удаленного пользователя.
	"""
	query = delete(User).where(users.c.id == user_id)
	await db.execute(query)
	await db.commit()

	logger.info(f"User ID: {user_id} was successfully deleted by user {action_by.email} with ID "
				f"{action_by.id}")

	return {"deleted_user_id": user_id}
