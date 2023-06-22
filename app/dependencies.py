from fastapi.security import OAuth2PasswordBearer
from .exceptions import CredentialsException
from fastapi import Depends
from typing import Annotated
from jose import JWTError, jwt
import config
from . import schemas
from .models.users import User
from .database import db

# dependency that expects for token from user
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(
	token: Annotated[str, Depends(oauth2_scheme)]
) -> schemas.UserInDB:
	"""
	Функция для декодирования получаемого от пользователя токена.
	Если токен не содержит email или не поддается декодированию, поднимается ошибка авторизации.
	Если токен корректный, но нет пользователя с указанным email - тоже.
	Эта функция в dependency, потому что будет по дефолту срабатывать при каждом запросе от пользователей.
	"""
	try:
		payload = jwt.decode(token=token, key=config.JWT_SECRET_KEY, algorithms=[config.JWT_SIGN_ALGORITHM])
		email: str | None = payload.get("sub")  # sub is std jwt token data param
		if email is None:
			raise CredentialsException()
		token_data = schemas.TokenData(email=email)
	except JWTError:
		raise CredentialsException()
	user = await User.get_user_by_email(db=db, email=token_data.email)
	if user is None:
		raise CredentialsException()
	return user
