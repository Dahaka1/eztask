import datetime
from typing import Any

from httpx import AsyncClient, Response
from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import User, users
from app.models.day_ratings import DayRating, day_ratings
from app.utils import sa_object_to_dict


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
	return utc_datetime.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)


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
	Если пригодится, можно будет добавить поиск пользователя
	 (для этого пока нет http-метода).
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


async def delete_day_rating(
	user_id: int,
	date: str,
	headers: dict,
	async_client: AsyncClient,
	raise_error: bool = False
) -> None:
	"""
	Удаляет оценку дня по дате. Дата - isoformat.
	"""
	response = await async_client.delete(
			f"/api/v1/day_ratings/user/{user_id}?date={date}",
			headers=headers
		)
	if raise_error is True:
		if response.status_code != 200:
			raise AssertionError(f"Can't delete day rating: server response "
								 f"status code is {response.status_code}")


async def change_day_rating_params(
	user_id: int,
	date: datetime.date | str,
	sa_session: AsyncSession,
	**kwargs
):
	"""
	Kwargs - любые параметры оценки дня, которые нужно установить.
	Date - можно передать в isoformat'е
	"""
	if isinstance(date, str):
		date = datetime.date.fromisoformat(date)
	query = update(DayRating).where(
		(day_ratings.c.user_id == user_id) &
		(day_ratings.c.date == date)
	).values(**kwargs)

	await sa_session.execute(query)
	await sa_session.commit()


# async def get_user_by_id(
# 	user_id: int,
# 	sa_session: AsyncSession
# ) -> dict | None:
# 	"""
# 	Поиск пользователя по ИД напрямую в БД.
# 	"""
# 	query = select(User).where(users.c.id == user_id)
#
# 	user_response = await sa_session.execute(query)
#
# 	user: dict | None = user_response.scalar()
#
# 	if user is None:
# 		return
#
# 	return sa_object_to_dict(user)

# async def change_note_data(note_id: int, sa_session: AsyncSession, **kwargs) -> None:
# 	"""
# 	Изменение параметров заметки по ИД.
# 	"""
# 	query = update(Note).where(notes.c.id == note_id).values(
# 		**kwargs
# 	)
# 	await sa_session.execute(query)
