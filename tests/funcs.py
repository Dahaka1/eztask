from httpx import AsyncClient, Response
from app.models.users import User, users
from sqlalchemy import insert, select, update
from typing import Any
from datetime import datetime, timezone
import random
from sqlalchemy.ext.asyncio import AsyncSession
import datetime


async def get_user_token(
	email: str,
	password: str,
	async_client: AsyncClient
) -> str:

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
	async_client: AsyncClient
) -> dict[str, Any]:
	user_data = dict(user={
		"email": email,
		"password": password,
		"first_name": firstname
	})

	response = await async_client.post(
		"/api/v1/users/",
		json=user_data
	)

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
	json: bool = False
) -> Response | dict[str, Any]:

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

	return response if json is False else response.json()


async def change_user_params(
	user_id: int,
	sa_session: AsyncSession,
	disabled: bool | None = None,
	is_staff: bool | None = None
) -> None:

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

	await change_user_params(user_id=user_id, sa_session=sa_session,
							 disabled=True)

	response_disabled_user = await endpoint_get_response(method, url, headers, async_test_client)

	await change_user_params(user_id, sa_session, False)

	headers = {"Authorization": "Bearer qwerty"}  # можно сделать не qwerty, а реальный токен, но с несуществующим email

	response_bad_token = await endpoint_get_response(method, url, headers, async_test_client)

	return response_bad_token, response_disabled_user


async def endpoint_get_response(method: str, url: str, headers: dict, async_test_client: AsyncClient):
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
	return utc_datetime.replace(tzinfo=timezone.utc).astimezone(tz=None)


def convert_obj_creating_time(obj_json: dict[str, Any], obj_type: str) -> str:
	"""
	:param obj_json: obj json data from response
	:param obj_type: note/user
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


def convert_creating_time_for_objects_list(*args, obj_type: str) -> tuple[list, ...]:
	match obj_type:
		case "note":
			for lst in args:
				for note in lst:
					note["created_at"] = convert_obj_creating_time(obj_json=note, obj_type=obj_type)

	return args

