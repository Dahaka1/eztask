import sqlalchemy
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean
from ..database import Base
from sqlalchemy.orm import relationship


class Task(Base):
	"""
	Модель задачи - то же, что и заметка, но может быть не завершена/завершена.
	"""
	__tablename__ = "tasks"

	id = Column(Integer, primary_key=True, index=True)
	text = Column(String(length=1000))
	date = Column(Date)
	user_id = Column(Integer, ForeignKey("users.id"))
	completed = Column(Boolean, default=False)

	user = relationship("User", back_populates="notes")


# sqlalchemy Table instance for using SA core queries with databases package
tasks: sqlalchemy.Table = Task.__table__
