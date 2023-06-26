from .. import schemas
from ..models.day_ratings import day_ratings
from ..database import db
from loguru import logger
import datetime


async def create_day_rating(day_rating: schemas.DayRatingCreate):
	"""
	Создание оценки дня.
	"""
	day_rating_dict = day_rating.dict()
	day_rating_dict.setdefault("date", datetime.date.today())
	query = day_ratings.insert().values(
		day_rating_dict
	)
	await db.execute(query)

	logger.info(f"Day rating for date {datetime.date.today()} was "
				f"successfully created by user with ID: {day_rating.user_id}")

	return day_rating_dict


async def get_day_ratings():
	"""
	Получение всех оценок дня.
	"""
	query = day_ratings.select().order_by(day_ratings.c.date)
	return await db.fetch_all(query)


async def get_day_ratings_me(current_user: schemas.User, filtering_params: dict[str, bool]):
	"""
	Получение всех собственных оценок дня пользователем.

	Если параметр в фильтре равен True, то делается фильтрация только по тем оценкам, где этот
	оценочный параметр ЗАПОЛНЕН (а не равен True)
	"""
	query = day_ratings.select().where(day_ratings.c.user_id == current_user.id).order_by(day_ratings.c.date)
	user_day_ratings = await db.fetch_all(query)
	if not any(filtering_params.values()):
		return user_day_ratings
	filters = [key for key, val in filtering_params.items() if val is True]

	return [
		rating for rating in user_day_ratings if
		all((rating[param] is not None for param in filters))
	]


async def update_day_rating(current_day_rating: schemas.DayRating, updated_day_rating: schemas.DayRatingUpdate):
	"""
	Обновление оценки дня.
	Изменить можно только оценочные bool-параметры.
	"""
	updated_day_rating.user_id = current_day_rating.user_id

	query = day_ratings.update().where(
		(day_ratings.c.user_id == current_day_rating.user_id) &
		(day_ratings.c.date == current_day_rating.date)
	).values(
		**updated_day_rating.dict()
	)

	await db.execute(query)

	logger.info(f"Day rating for date {current_day_rating.date} was successfully "
				f"updated by creator with ID: {current_day_rating.user_id}")

	return {**updated_day_rating.dict(), "date": current_day_rating.date}


async def delete_day_rating(day_rating: schemas.DayRating):
	"""
	Удаление оценки дня.
	"""
	query = day_ratings.delete().where(
		(day_ratings.c.user_id == day_rating.user_id) &
		(day_ratings.c.date == day_rating.date)
	)
	await db.execute(query)

	return day_rating
