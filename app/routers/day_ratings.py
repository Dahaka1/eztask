import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Body, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import schemas
from ..crud import crud_day_ratings
from ..dependencies import get_async_session
from ..dependencies import get_current_active_user, get_day_rating, get_day_rating_filters
from ..exceptions import PermissionsError
from ..models.day_ratings import DayRating

router = APIRouter(
	prefix="/day_ratings",
	tags=["day_ratings"]
)


@router.post("/", response_model=schemas.DayRating, status_code=status.HTTP_201_CREATED)
async def create_day_rating(
	current_user: Annotated[schemas.User, Depends(get_current_active_user)],
	day_rating: Annotated[schemas.DayRatingCreate, Body(embed=True)],
	db: Annotated[AsyncSession, Depends(get_async_session)]
):
	"""
	Добавление оценки дня пользователем.
	Нужен как минимум один указанный bool-параметр.
	Дата определяется по умолчанию текущая.

	Добавить оценку дня по дате, если она уже есть, нельзя.
	В таком случае можно только изменить существующую (см. 'put').
	"""
	day_rating.user_id = current_user.id

	if not await DayRating.check_day_rating_params(day_rating):
		needed_params = list(day_rating.dict())
		needed_params.remove("user_id")
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
							detail=f"Day rating must contains at least one of rating params {needed_params}")

	day_rating_exists = await DayRating.get_day_rating(user_id=day_rating.user_id,
													   date=datetime.date.today(),
													   db=db)

	if day_rating_exists is not None:
		raise HTTPException(status_code=status.HTTP_409_CONFLICT,
							detail=f"Day rating for date {datetime.date.today()} already exists. "
								   f"Use the 'put'-method instead of 'post'")

	return await crud_day_ratings.create_day_rating(day_rating, db=db)


@router.get("/", response_model=list[schemas.DayRating])
async def read_day_ratings(
	current_user: Annotated[schemas.User, Depends(get_current_active_user)],
	db: Annotated[AsyncSession, Depends(get_async_session)]
):
	"""
	Получение списка всех оценок дня. Доступно только для is_staff-пользователей.
	"""
	if not current_user.is_staff:
		raise PermissionsError()
	return await crud_day_ratings.get_day_ratings(db=db)


@router.get("/me", response_model=list[schemas.DayRating])
async def read_day_ratings_me(
	current_user: Annotated[schemas.User, Depends(get_current_active_user)],
	filtering: Annotated[dict[str, bool], Depends(get_day_rating_filters)],
	db: Annotated[AsyncSession, Depends(get_async_session)]
):
	"""
	Получение пользователем списка оценок дня.
	Возможно указать параметры фильтрации по заполненности полей в БД (оценочных bool-полей).
	Параметры получаются в dependencies.get_day_rating_filters.

	Если параметр в фильтре равен True, то делается фильтрация только по тем оценкам, где этот
	оценочный параметр ЗАПОЛНЕН (а не равен True).

	Если понадобится, в дальнейшем можно добавить фильтрацию именно по значениям параметров.
	"""
	return await crud_day_ratings.get_day_ratings_me(current_user, filtering, db=db)


@router.put("/user/{user_id}", response_model=schemas.DayRating)
async def update_day_rating(
	current_user: Annotated[schemas.User, Depends(get_current_active_user)],
	current_day_rating: Annotated[schemas.DayRating, Depends(get_day_rating)],
	day_rating: Annotated[schemas.DayRatingUpdate, Body(embed=True, title="Updated day rating")],
	db: Annotated[AsyncSession, Depends(get_async_session)]
):
	"""
	Обновление оценки дня пользователем. Доступно только для создателя оценки.

	Оценка дня находится по:
	- Переданному в пути ИД пользователя;
	- Переданной дате оценки дня в качестве параметра запроса (?date=X).
	"""
	if current_user.id != current_day_rating.user_id:
		raise PermissionsError()
	if not await DayRating.check_day_rating_params(day_rating):
		needed_params = list(day_rating.dict())
		needed_params.remove("user_id")
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
							detail=f"Day rating must contains at least one of rating params {needed_params}")
	return await crud_day_ratings.update_day_rating(current_day_rating, day_rating, db=db)


@router.get("/user/{user_id}", response_model=schemas.DayRating)
async def read_day_rating(
	current_user: Annotated[schemas.User, Depends(get_current_active_user)],
	current_day_rating: Annotated[schemas.DayRating, Depends(get_day_rating)]
):
	"""
	Получение оценки дня пользователем (см. put-метод по этому маршруту).
	"""
	if current_user.id != current_day_rating.user_id:
		raise PermissionsError()
	return current_day_rating


@router.delete("/user/{user_id}", response_model=schemas.DayRating)
async def delete_day_rating(
	current_user: Annotated[schemas.User, Depends(get_current_active_user)],
	current_day_rating: Annotated[schemas.DayRating, Depends(get_day_rating)],
	db: Annotated[AsyncSession, Depends(get_async_session)]
):
	"""
	Удаление оценки дня (см. put- и get-методы по этому маршруту)
	"""
	if current_user.id != current_day_rating.user_id:
		raise PermissionsError()
	return await crud_day_ratings.delete_day_rating(current_day_rating, db=db)
