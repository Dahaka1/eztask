import sqlalchemy
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from ..database import Base
from sqlalchemy.orm import relationship


class Note(Base):
	"""
	Модель заметки.
	"""
	__tablename__ = "notes"

	id = Column(Integer, primary_key=True, index=True)
	text = Column(String(length=1000))
	date = Column(Date)
	user_id = Column(Integer, ForeignKey("users.id"))

	user = relationship("User", back_populates="notes")


# sqlalchemy Table instance for using SA core queries with databases package
notes: sqlalchemy.Table = Note.__table__
