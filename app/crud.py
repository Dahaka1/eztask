from . import schemas
from .models.users import users
from .database import db
from .utils import get_password_hash


async def create_user(user: schemas.UserCreate):
	"""
	:return: Возвращает словарь с данными созданного юзера.
	Далее он возвращается функцией post-метода в виде pydantic-модели.
	"""
	hashed_password = get_password_hash(user.password)
	query = users.insert().values(
		email=user.email,
		first_name=user.first_name,
		last_name=user.last_name,
		hashed_password=hashed_password
	)
	user_id = await db.execute(query)

	return {
		**user.dict(), "id": user_id
	}
