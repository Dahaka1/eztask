from httpx import AsyncClient, Response
from app.models.users import User, users
from sqlalchemy import update
from typing import Any
from datetime import datetime, timezone
import random
from sqlalchemy.ext.asyncio import AsyncSession
import datetime
from app.models.notes import Note, notes


async def get_user_token(
	email: str,
	password: str,
	async_client: AsyncClient
) -> str:
	"""
	Авторизация пользователя для тестов.
	"""
	auth_response = await async_client.post(
		"/api/v1/token/",
		data={"email": email,
			  "password": password}
	)

	return auth_response.json()["access_token"]


async def create_user(
	email: str,
	password: str,
	firstname: str,
	async_client: AsyncClient,
	raise_error: bool = False
) -> dict[str, Any]:
	"""
	Создание пользователя для тестов и получение его токена авторизации.

	Функция использует для создания юзера Post-метод, который тестируется непосредственно в тестах.
	Поэтому здесь добавил дополнительное тестирование: если raise_error = True (это нужно в позитивных тестах),
	 то при неудачном создании объекта рейзится ошибка на уровне этой функции.
	"""
	user_data = dict(user={
		"email": email,
		"password": password,
		"first_name": firstname
	})

	response = await async_client.post(
		"/api/v1/users/",
		json=user_data
	)
	if raise_error is True:
		if response.status_code != 201:
			raise AssertionError(f"Can't create a new user: server response status code is {response.status_code}")
	result = {
		** response.json(),
		"token": await get_user_token(email, password, async_client)
	}

	return result


async def create_random_note(
	headers: dict,
	async_client: AsyncClient,
	note_type: str = "note",
	date: datetime.date = datetime.date.today(),
	json: bool = False,
	raise_error: bool = False
) -> Response | dict[str, Any]:
	"""
	Создание рандомной заметки для тестов.
	Опционально можно указать ее тип и дату.
	Можно опционально получить json ответа, а не ответ.

	Функция использует для создания юзера Post-метод, который тестируется непосредственно в тестах.
	Поэтому здесь добавил дополнительное тестирование: если raise_error = True (это нужно в позитивных тестах),
	 то при неудачном создании объекта рейзится ошибка на уровне этой функции.
	"""

	words = "apple gold machine guitar city"

	response = await async_client.post(
		"/api/v1/notes/",
		json=dict(note={
			"text": random.choice(words.split()),
			"note_type": note_type,
			"date": date.isoformat()
		}),
		headers=headers
	)
	if raise_error is True:
		if response.status_code != 201:
			raise AssertionError(f"Can't create a new note: server response status code is {response.status_code}")

	return response if json is False else response.json()


async def create_random_notes(
	headers: dict,
	async_client: AsyncClient,
	amount: int = 10
) -> None:
	"""
	Создает список рандомных заметок для пользователя.
	"""
	for _ in range(amount):
		note_type = random.choice(("task", "note"))
		note_date = datetime.date.today() + datetime.timedelta(days=random.randrange(10))
		await create_random_note(
			headers=headers, async_client=async_client, date=note_date,
			note_type=note_type, raise_error=True
		)


async def change_user_params(
	user_id: int,
	sa_session: AsyncSession,
	disabled: bool | None = None,
	is_staff: bool | None = None
) -> None:
	"""
	Изменить параметры пользователя в БД для тестов.
	"""

	queries = []

	if disabled is not None:
		query = update(User).where(users.c.id == user_id).values(
			disabled=disabled
		)
		queries.append(query)

	if is_staff is not None:
		query = update(User).where(users.c.id == user_id).values(
			is_staff=is_staff
		)
		queries.append(query)

	for q in queries:
		await sa_session.execute(q)
		await sa_session.commit()


async def endpoint_autotest(data: dict[str, Any]) -> tuple[Response, Response]:
	"""
	Функция для сокращения количества кода в test_auth. Запускает endpoint_test с переданными
	 в словаре параметрами.
	"""
	url = data.get("url")
	headers = data.get("headers")
	user_id = data.get("user_id")
	sa_session = data.get("sa_session")
	async_test_client = data.get("async_test_client")
	method = data.get("method")

	return await endpoint_test(method, url, headers, user_id, sa_session, async_test_client)


async def endpoint_test(method: str, url: str, headers: dict[str, str],
						user_id: int, sa_session: AsyncSession,
						async_test_client: AsyncClient) -> tuple[Response, Response]:
	"""
	Тестирует эндпоинт на получение ошибок, если пользователь не авторизован или заблокирован.
	"""
	await change_user_params(user_id=user_id, sa_session=sa_session,
							 disabled=True)

	response_disabled_user = await endpoint_get_response(method, url, headers, async_test_client)

	await change_user_params(user_id, sa_session, False)

	headers = {"Authorization": "Bearer qwerty"}  # можно сделать не qwerty, а реальный токен, но с несуществующим email

	response_bad_token = await endpoint_get_response(method, url, headers, async_test_client)

	return response_bad_token, response_disabled_user


async def endpoint_get_response(method: str, url: str, headers: dict, async_test_client: AsyncClient):
	"""
	В зависимости от метода возвращает ответ от апи.
	Используется только в endpoint_test для сокращения количества кода в test_auth.
	"""
	match method:
		case "get":
			return await async_test_client.get(url, headers=headers)
		case "post":
			return await async_test_client.post(url, headers=headers)
		case "put":
			return await async_test_client.put(url, headers=headers)
		case "delete":
			return await async_test_client.put(url, headers=headers)
		case _:
			raise AttributeError


def convert_utc_datetime_to_local(utc_datetime: datetime.datetime):
	"""
	В БД хранится дата/время с utc-00.
	Эта функция конвертирует их в локальные (+03).
	"""
	return utc_datetime.replace(tzinfo=timezone.utc).astimezone(tz=None)


def convert_obj_creating_time(obj_json: dict[str, Any], obj_type: str) -> str:
	"""
	Конвертирует время создания объекта (заметки/пользователя) в местное.
	Возвращает isoformat даты/времени (строку).

	:param obj_json: obj json data from response
	:param obj_type: 'note'/'user'
	"""
	match obj_type:
		case "note":
			creating_datetime = obj_json.get("created_at")
		case "user":
			creating_datetime = obj_json.get("registered_at")
		case _:
			raise AttributeError
	creating_datetime_obj = datetime.datetime.fromisoformat(creating_datetime)
	local_creating_datetime = convert_utc_datetime_to_local(creating_datetime_obj).isoformat()

	return local_creating_datetime


def exclude_datetime_creating(obj: list[dict[str, Any]] | dict[str, Any], obj_type: str) -> \
		list[dict[str, Any]] | dict[str, Any]:
	"""
	Исключает дату/время создания объекта (-ов) из данных.
	Делаю этот костыль для избегания сравнивания даты/времени создания объектов.
	Потом можно реализовать нормально.

	Принимает список словарей / словарь.
	:param obj: Objects list / object instance
	:param obj_type: 'note'/'user'.
	"""
	match type(obj).__name__:
		case "list":
			obj_list = obj
			for item in obj_list:
				match obj_type:
					case "note":
						item.pop("created_at")
					case "user":
						item.pop("registered_at")
		case "dict":
			match obj_type:
				case "note":
					obj.pop("created_at")
				case "user":
					obj.pop("registered_at")
	return obj


async def get_obj_by_id(obj_id: int, obj_type: str, headers: dict, async_client: AsyncClient) -> Response:
	"""
	Получить данные заметки по ИД.
	Если пригодится, можно будет добавить поиск пользователя.
	"""
	match obj_type:
		case "note":
			obj_response = await async_client.get(
				f"/api/v1/notes/{obj_id}",
				headers=headers
			)
		case _:
			raise AttributeError

	return obj_response


# async def change_note_data(note_id: int, sa_session: AsyncSession, **kwargs) -> None:
# 	"""
# 	Изменение параметров заметки по ИД.
# 	"""
# 	query = update(Note).where(notes.c.id == note_id).values(
# 		**kwargs
# 	)
# 	await sa_session.execute(query)
