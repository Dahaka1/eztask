import config
from datetime import timedelta, datetime
from jose import jwt


def verify_password(password, hashed_password) -> bool:
	"""
	Сравнение хешей паролей.
	"""
	return config.pwd_context.verify(password, hashed_password)


def get_password_hash(password) -> str:
	"""
	Хеширование пароля.
	"""
	return config.pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)):
	"""
	Создание JWT-токена. "Живет" в течение переданного времени. По умолчанию время указывается в конфиге.
	В data должен содержаться обязательный для JWT-токена параметр: "sub" (субъект - имя пользователя/email/...).
	"""
	expire = datetime.utcnow() + expires_delta
	data.update({"exp": expire})  # std jwt data param
	encoded_jwt = jwt.encode(claims=data, key=config.JWT_SECRET_KEY, algorithm=config.JWT_SIGN_ALGORITHM)
	return encoded_jwt
