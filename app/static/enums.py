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


class PollingTypeEnum(Enum):
	"""
	Типы рандомных опроса для пользователя.

	Примеры опросов:
	- Note: "Вам помогают или помогли сегодня заметки?" (если по текущему дню они были);
	- Task: "Сегодня получилось выполнить все задачи?" (если были);
	- Health: "Ваше самочувствие сегодня удовлетворительное?";
	- Next_Day_Expectations: "Завтра будет хороший день?";
	- Mood: "Какое сегодня было настроение?".
	"""
	note = "note"
	task = "task"
	health = "health"
	next_day_expectations = "next_day_expectations"
	mood = "mood"
