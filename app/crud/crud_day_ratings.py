from .. import schemas
from loguru import logger
import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.day_ratings import DayRating, day_ratings
from sqlalchemy import insert, select, update, delete
from ..utils import sa_objects_dicts_list


async def create_day_rating(day_rating: schemas.DayRatingCreate, db: AsyncSession):
	"""
	Создание оценки дня.
	"""
	day_rating_dict = day_rating.dict()
	day_rating_dict.setdefault("date", datetime.date.today())
	query = insert(DayRating).values(
		**day_rating_dict
	)
	await db.execute(query)
	await db.commit()

	logger.info(f"Day rating for date {datetime.date.today()} was "
				f"successfully created by user with ID: {day_rating.user_id}")

	return day_rating_dict


async def get_day_ratings(db: AsyncSession):
	"""
	Получение всех оценок дня.
	"""
	query = select(DayRating).order_by(day_ratings.c.date)
	result = await db.execute(query)
	return sa_objects_dicts_list(result.scalars().all())


async def get_day_ratings_me(current_user: schemas.User, filtering_params: dict[str, bool], db: AsyncSession):
	"""
	Получение всех собственных оценок дня пользователем.

	Если параметр в фильтре равен True, то делается фильтрация только по тем оценкам, где этот
	оценочный параметр ЗАПОЛНЕН (а не равен True)
	"""
	query = select(DayRating).where(day_ratings.c.user_id == current_user.id).order_by(day_ratings.c.date)
	result = await db.execute(query)
	user_day_ratings = sa_objects_dicts_list(result.scalars().all())
	if not any(filtering_params.values()):
		return user_day_ratings
	filters = [key for key, val in filtering_params.items() if val is True]

	return [
		rating for rating in user_day_ratings if
		all((rating[param] is not None for param in filters))
	]


async def update_day_rating(current_day_rating: schemas.DayRating,
							updated_day_rating: schemas.DayRatingUpdate,
							db: AsyncSession):
	"""
	Обновление оценки дня.
	Изменить можно только оценочные bool-параметры.
	"""
	updated_day_rating.user_id = current_day_rating.user_id

	current_day_rating_dict = current_day_rating.dict()
	for key, val in updated_day_rating.dict().items():
		if val is not None:
			current_day_rating_dict[key] = val

	query = update(DayRating).where(
		(day_ratings.c.user_id == current_day_rating.user_id) &
		(day_ratings.c.date == current_day_rating.date)
	).values(
		**current_day_rating_dict
	)

	await db.execute(query)
	await db.commit()

	logger.info(f"Day rating for date {current_day_rating.date} was successfully "
				f"updated by creator with ID: {current_day_rating.user_id}")

	return {**current_day_rating_dict, "date": current_day_rating.date}


async def delete_day_rating(day_rating: schemas.DayRating, db: AsyncSession):
	"""
	Удаление оценки дня.
	"""
	query = delete(DayRating).where(
		(day_ratings.c.user_id == day_rating.user_id) &
		(day_ratings.c.date == day_rating.date)
	)
	await db.execute(query)
	await db.commit()

	logger.info(f"Day rating for date {datetime.date.today()} was "
				f"successfully deleted by user with ID: {day_rating.user_id}")

	return day_rating
