from sqlalchemy import Column, Integer, String, ForeignKey, Date, Boolean
from .database import Base
from sqlalchemy.orm import relationship

# TODO: после доработки функций с текущими моделями
#  добавить оценку прошедшего дня для пользователя (по разным параметрам)


class User(Base):
	"""
	 Модель пользователя
	TODO: добавить поле ТГ-аккаунта, если буду интегрировать поддержку ТГ
	TODO: добавить поля для аутентификационных данных
	"""
	__tablename__ = "users"

	id = Column(Integer, primary_key=True, index=True)
	email = Column(String(length=50), unique=True, index=True)
	first_name = Column(String(length=50))
	last_name = Column(String(length=50), nullable=True, default=None)
	hashed_password = Column(String)
	
	notes = relationship("Note", back_populates="user")
	tasks = relationship("Task", back_populates="user")


class Note(Base):
	"""
	Модель заметки
	"""
	__tablename__ = "notes"

	id = Column(Integer, primary_key=True, index=True)
	text = Column(String(length=1000))
	date = Column(Date)
	user_id = Column(Integer, ForeignKey("users.id"))

	user = relationship("User", back_populates="notes")


class Task(Base):
	"""
	Модель задачи - то же, что и заметка, но может быть не завершена/завершена
	"""
	__tablename__ = "tasks"

	id = Column(Integer, primary_key=True, index=True)
	text = Column(String(length=1000))
	date = Column(Date)
	user_id = Column(Integer, ForeignKey("users.id"))
	completed = Column(Boolean, default=False)

	user = relationship("User", back_populates="notes")


# sqlalchemy Table instances
users, notes, tasks = User.__table__, Note.__table__, Task.__table__
