from pydantic import BaseModel, Field, EmailStr
import datetime


class Token(BaseModel):
	access_token: str
	token_type: str


class TokenData(BaseModel):
	email: str | None = None


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
	email: EmailStr = Field(
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
	is_staff: bool | None = Field(
		title="True if user has staff-permissions",
		default=False
	)
	disabled: bool | None = Field(
		title="False if user is active and non-blocked",
		default=False
	)
	notes: list[Note] = []
	tasks: list[Task] = []

	class Config:
		orm_mode = True


class UserInDB(User):
	hashed_password: str


class UserUpdate(BaseModel):
	email: EmailStr | None = Field(
		title="User's email",
		example="ijoech@gmail.com",
		default=None
	)
	first_name: str | None = Field(
		max_length=50,
		title="User first name, required",
		example="Yaroslav",
		default=None
	)
	last_name: str | None = Field(
		max_length=50,
		title="User last name, optional",
		example="Ivanov",
		default=None
	)
	password: str | None = Field(
		min_length=8,
		default=None
	)
	disabled: bool | None = Field(
		title="False if user is active and non-blocked",
		default=False
	)
