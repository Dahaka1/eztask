import datetime
from typing import Optional

from sqlalchemy import Column, Integer, Boolean, Date, ForeignKey, PrimaryKeyConstraint, select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import schemas
from ..database import Base


class DayRating(Base):
	__tablename__ = "day_ratings"
	__table_args__ = (
		PrimaryKeyConstraint("user_id", "date", name="user_date_pkey"),
	)

	user_id = Column(Integer, ForeignKey("users.id"))
	date = Column(Date)
	notes = Column(Boolean, nullable=True)
	mood = Column(Boolean, nullable=True)
	next_day_expectations = Column(Boolean, nullable=True)
	health = Column(Boolean, nullable=True)

	@staticmethod
	async def check_day_rating_params(day_rating: schemas.DayRatingBase):
		if all(
			(param is None for param in
			 (day_rating.notes, day_rating.mood,
			  day_rating.next_day_expectations, day_rating.health))
		):
			return False
		return True

	@staticmethod
	async def get_day_rating(user_id: int, date: datetime.date, db: AsyncSession) -> Optional[schemas.DayRating]:
		query = select(DayRating).where(
				(DayRating.date == date) &
				(DayRating.user_id == user_id)
			)
		existing_day_rating = await db.execute(query)
		return existing_day_rating.scalar()
