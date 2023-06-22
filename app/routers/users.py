from fastapi import APIRouter, Body, HTTPException, status, Depends
from .. import schemas, crud
from ..models.users import users
from ..database import db
from typing import Annotated
from ..dependencies import get_current_user


router = APIRouter(
	prefix="/users",
	tags=["users"]
)


@router.post("/register", response_model=schemas.User)
async def create_user(
	user: Annotated[schemas.UserCreate, Body(embed=True, title="User params dict key")]
):
	"""
	Регистрация пользователя по email.
	"""
	query = users.select().where(users.c.email == user.email)
	existing_user = await db.execute(query)
	if existing_user:
		raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
	return await crud.create_user(user)


@router.get("/me", response_model=schemas.User)
async def read_users_me(
	current_user: Annotated[schemas.User, Depends(get_current_user)]
):
	"""
	Получение данных аккаунта пользователем после проверки его токена.
	"""
	return current_user

