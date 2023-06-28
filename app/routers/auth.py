from fastapi import APIRouter, HTTPException, status
from .. import schemas
from typing import Annotated
from fastapi import Form, Depends
from ..models.users import User
from ..exceptions import CredentialsException
from .. import utils
from loguru import logger
from ..dependencies import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(
	prefix="/token",
	tags=["auth_token"]
)


@router.post("/", response_model=schemas.Token)
async def login_for_access_token(
	email: Annotated[str, Form()],
	password: Annotated[str, Form()],
	db: Annotated[AsyncSession, Depends(get_async_session)]
):
	"""
	Метод проверяет логин и пароль пользователя при авторизации.
	Если они верны, то создает access_token (JWT token) и возвращает его.
	"""
	user = await User.authenticate_user(
		db=db, email=email, password=password
	)
	if not user:
		raise CredentialsException(detail="Incorrect username or password")

	if user.disabled:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Disabled user")

	access_token = utils.create_access_token(
		data={"sub": user.email}
	)

	logger.info(f"User {email} (ID: {user.id}) was successfully authorized")

	return {"access_token": access_token, "token_type": "bearer"}



