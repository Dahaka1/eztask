from fastapi import APIRouter
from .. import schemas
from typing import Annotated
from fastapi import Form
from ..models.users import User
from ..database import db
from ..exceptions import CredentialsException
from .. import utils
from .. import logger


router = APIRouter(
	prefix="/token",
	tags=["auth_token"]
)


@router.post("/", response_model=schemas.Token)
async def login_for_access_token(
	email: Annotated[str, Form()],
	password: Annotated[str, Form()]
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
	access_token = utils.create_access_token(
		data={"sub": user.email}
	)
	logger.info(f"User {email} (ID: {user.id}) was successfully authorized")
	return {"access_token": access_token, "token_type": "bearer"}



