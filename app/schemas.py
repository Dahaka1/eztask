from pydantic import BaseModel, Field, EmailStr
import datetime
from .static.enums import NoteTypeEnumDB, NotesCompletedEnum, \
	NotesOrderByEnum, NotesPeriodEnum, NoteTypeEnum
from typing import Optional


class Token(BaseModel):
	access_token: str
	token_type: str


class TokenData(BaseModel):
	email: Optional[str] = None


class NoteBase(BaseModel):
	note_type: Optional[NoteTypeEnumDB] = Field(
		title="Note type - note/task",
		example="task",
		default=NoteTypeEnumDB.note.value
	)
	text: str = Field(
		max_length=1000,
		title="Note/task content field",
		example="Needs for walking today"
	)
	date: Optional[datetime.date] = Field(
		title="Note/task date",
		description="Current date by default",
		default_factory=datetime.date.today
	)
	created_at: Optional[datetime.datetime] = Field(
		title="Note creating datetime",
		description="Current date/time by default",
		default_factory=datetime.datetime.now
	)
	user_id: Optional[int] = Field(ge=1)


class NoteCreate(NoteBase):
	"""
	ИД пользователя определяется в момент создания заметки (после проверки токена)
	"""
	pass


class Note(NoteBase):
	id: int = Field(ge=1)
	completed: Optional[bool] = Field(
		title="Is task completed?",
		description="Note could be completed if its type is task.\n"
					"If note type is standard note, this field is null."
	)

	class Config:
		orm_mode = True


class NoteUpdate(BaseModel):
	note_type: Optional[NoteTypeEnumDB] = Field(
		title="Note type - note/task",
		example=NoteTypeEnumDB.task.value,
		default=None
	)
	text: Optional[str] = Field(
		max_length=1000,
		title="Note/task content field",
		example="Needs for walking today",
		default=None
	)
	date: Optional[datetime.date] = Field(
		title="Note/task date",
		default=None
	)
	completed: Optional[bool] = None


class UserBase(BaseModel):
	email: EmailStr = Field(
		title="User's email",
		example="ijoech@gmail.com"
	)
	first_name: str = Field(
		max_length=50,
		title="User first name, required",
		example="Yaroslav"
	)
	last_name: Optional[str] = Field(
		max_length=50,
		title="User last name, optional",
		example="Ivanov",
		default=None
	)
	registered_at: Optional[datetime.datetime] = Field(
		default_factory=datetime.datetime.now
	)


class UserCreate(UserBase):
	password: str = Field(min_length=8)


class User(UserBase):
	id: int = Field(ge=1)
	is_staff: Optional[bool] = Field(
		title="True if user has staff-permissions",
		default=False
	)
	disabled: Optional[bool] = Field(
		title="False if user is active and non-blocked",
		default=False
	)
	notes: Optional[list[Note]] = None

	class Config:
		orm_mode = True


class UserInDB(User):
	hashed_password: str


class UserUpdate(BaseModel):
	email: Optional[EmailStr] = Field(
		title="User's email",
		example="ijoech@gmail.com",
		default=None
	)
	first_name: Optional[str] = Field(
		max_length=50,
		title="User first name, required",
		example="Yaroslav",
		default=None
	)
	last_name: Optional[str] = Field(
		max_length=50,
		title="User last name, optional",
		example="Ivanov",
		default=None
	)
	password: Optional[str] = Field(
		min_length=8,
		default=None
	)
	disabled: Optional[bool] = Field(
		description="False if user is active and non-blocked",
		default=False
	)


class GetNotesParams(BaseModel):
	sorting: NotesOrderByEnum | None = NotesOrderByEnum.date_asc
	period: NotesPeriodEnum | None = NotesPeriodEnum.upcoming
	type: NoteTypeEnum | None = NoteTypeEnum.all
	completed: NotesCompletedEnum | None = NotesCompletedEnum.all


class DayRatingBase(BaseModel):
	user_id: Optional[int] = Field(ge=1)
	notes: Optional[bool] = Field(
		description="Rating for tasks of the day (done or not, etc.)",
		default=None
	)
	mood: Optional[bool] = Field(
		description="Rating for mood of the day",
		default=None
	)
	health: Optional[bool] = Field(
		description="Rating for health feeling of the day",
		default=None
	)
	next_day_expectations: Optional[bool] = Field(
		description="Positive or negative expectations from the next day",
		default=None
	)


class DayRatingCreate(DayRatingBase):
	pass


class DayRating(DayRatingBase):
	date: datetime.date = Field(
		description="Date that was rated by user"
	)


class DayRatingUpdate(DayRatingBase):
	pass
