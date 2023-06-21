from pydantic import BaseModel, Field
import datetime


class NoteBase(BaseModel):
	text: str = Field(
		max_length=1000,
		title="Note/task content field",
		example="Needs for walking today"
	)
	date: datetime.date | None = Field(
		title="Note/task date",
		description="Current date by default"
	)


class NoteCreate(NoteBase):
	user_id: int = Field(ge=1)


class Note(NoteCreate):
	id: int = Field(ge=1)

	class Config:
		orm_mode = True


class TaskBase(NoteBase):
	completed: bool | None = Field(
		default=False,
		title="Is task completed?"
	)


class TaskCreate(TaskBase, NoteCreate):
	pass


class Task(Note):
	pass


class UserBase(BaseModel):
	email: str = Field(
		max_length=50,
		title="User's email",
		example="ijoech@gmail.com"
	)
	first_name: str = Field(
		max_length=50,
		title="User first name, required",
		example="Yaroslav"
	)
	last_name: str | None = Field(
		max_length=50,
		title="User last name, optional",
		example="Ivanov",
		default=None
	)


class UserCreate(UserBase):
	password: str = Field(min_length=8)


class User(UserBase):
	id: int = Field(ge=1)
	notes: list[Note] = []

	class Config:
		orm_mode = True
