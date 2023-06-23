from fastapi import APIRouter, Body, HTTPException, status, Depends
from .. import schemas
from ..models.users import users, User
from ..database import db
from typing import Annotated
from ..dependencies import get_current_active_user, get_user_id
from ..exceptions import PermissionsError
from ..crud import crud_users


router = APIRouter(
	prefix="/users",
	tags=["users"]
)

# TODO: user retrieve by id (not by himself)


@router.get("/", response_model=list[schemas.User])
async def read_users(
	current_user: Annotated[schemas.User, Depends(get_current_active_user)]
):
	"""
	Получение списка всех пользователей
	"""
	if current_user.is_staff:
		return await crud_users.get_users()
	raise PermissionsError()


@router.post("/", response_model=schemas.User)
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
	return await crud_users.create_user(user)


@router.get("/me", response_model=schemas.User)
async def read_users_me(
	current_user: Annotated[schemas.User, Depends(get_current_active_user)]
):
	"""
	Получение данных аккаунта пользователем после проверки его токена.
	"""
	return current_user


@router.put("/{user_id}", response_model=schemas.User)
async def update_user(
	user: Annotated[schemas.UserUpdate, Body(embed=True, title="User updated params dict")],
	current_user: Annotated[schemas.User, Depends(get_current_active_user)],
	user_id: Annotated[int, Depends(get_user_id)]
):
	"""
	Обновление данных пользователя. Обновить данные могут:
	- сам пользователь;
	- стафф-пользователь.
	Права проверяются функцией check_user_permissions.
	TODO: решить, может ли стафф менять пароль у другого пользователя (сейчас может)
	"""
	if not await User.check_user_permissions(current_user=current_user, user_id=user_id):
		raise PermissionsError()
	if any(user.dict().values()):
		return await crud_users.update_user(user=user, user_id=user_id, action_by=current_user)
	else:
		return current_user


@router.delete("/{user_id}")
async def delete_user(
	current_user: Annotated[schemas.User, Depends(get_current_active_user)],
	user_id: Annotated[int, Depends(get_user_id)]
):
	"""
	см. update_user
	"""
	if not await User.check_user_permissions(current_user=current_user, user_id=user_id):
		raise PermissionsError()
	return await crud_users.delete_user(user_id=user_id, action_by=current_user)
