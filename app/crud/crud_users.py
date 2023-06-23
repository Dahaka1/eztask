from .. import schemas, logger
from ..models.users import users
from ..database import db
from ..utils import get_password_hash


async def get_users():
	"""
	:return: Возвращает список всех пользователей (pydantic-модели)
	"""
	query = users.select()
	return await db.fetch_all(query)


async def create_user(user: schemas.UserCreate):
	"""
	:return: Возвращает словарь с данными созданного юзера.
	"""
	hashed_password = get_password_hash(user.password)
	query = users.insert().values(
		email=user.email,
		first_name=user.first_name,
		last_name=user.last_name,
		hashed_password=hashed_password,
		is_staff=False,
		disabled=False
	)  # пришлось тут определить is_staff и disabled опять - почему-то дефолтные значения в
	# models.users.User не срабатывают :(
	user_id = await db.execute(query)

	logger.info(f"User {user.email} (ID: {user_id}) was successfully registered")

	return {
		**user.dict(), "id": user_id
	}


async def update_user(user: schemas.UserUpdate, user_id: int, action_by: schemas.User):
	"""
	:return: Возвращает словарь с данными обновленного пользователя.
	"""
	query = users.select().where(users.c.id == user_id)
	user_db = dict(await db.fetch_one(query))
	for key, val in user.dict().items():
		if not val is None:
			if key == "password":
				hashed_password = get_password_hash(val)
				user_db["hashed_password"] = hashed_password
			else:
				user_db[key] = val
	query = users.update().where(users.c.id == user_id).values(**user_db)
	await db.execute(query)

	logger.info(f"User {user_db['email']} (ID: {user_id}) was successfully updated by user "
				f"{action_by.email} with ID {action_by.id}")

	return user_db


async def delete_user(user_id: int, action_by: schemas.User) -> dict[str, int]:
	"""
	:return: Возвращает ИД удаленного пользователя.
	"""
	query = users.delete().where(users.c.id == user_id)
	await db.execute(query)

	logger.info(f"User ID: {user_id} was successfully deleted by user {action_by.email} with ID "
				f"{action_by.id}")

	return {"deleted_user_id": user_id}
