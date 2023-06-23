from enum import Enum


class NotesOrderByEnum(Enum):
	"""
	Сортировка заметок пользователя по дате
	"""
	date_asc = "date"
	date_desc = "-date"


class NotesPeriodEnum(Enum):
	"""
	Фильтрация по дате (например, upcoming - заметки/задачи после сегодняшнего дня).
	"""
	upcoming = "upcoming"
	past = "past"
	all = "all"


class NotesCompletedEnum(Enum):  # if notes type is "task"
	"""
	Фильтрация по статусу исполнения.
	Сработает только если выбран тип заметок "task" ("задача").
	"""
	completed = True  # upcoming task may be completed before their date
	non_completed = False
	all = None


class NoteTypeEnum(Enum):
	"""
	Фильтрация по типу заметок.
	"""
	note = "note"
	task = "task"
	all = "all"


class NoteTypeEnumDB(Enum):
	"""
	Заметка может быть стандартной заметкой, а может - задачей.
	Этот Enum для модели SA.
	"""
	note = "note"
	task = "task"
