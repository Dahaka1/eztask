import sqlalchemy
from sqlalchemy import Column, Integer, Boolean, Date, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from ..database import Base
from .. import schemas


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

	user = relationship("User", back_populates="day_ratings")

	@staticmethod
	async def check_day_rating_params(day_rating: schemas.DayRatingBase):
		if all(
			(param is None for param in
			 (day_rating.notes, day_rating.mood,
			  day_rating.next_day_expectations, day_rating.health))
		):
			return False
		return True


# sqlalchemy Table instance for using SA core queries with databases package
day_ratings: sqlalchemy.Table = DayRating.__table__
