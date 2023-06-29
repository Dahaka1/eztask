import random

from httpx import AsyncClient, Response

from .fills import create_user, create_random_note, create_random_day_rating


async def notes_rud_test(
	async_client: AsyncClient,
	method: str,
	current_user_headers: dict
) -> tuple[Response, ...]:
	"""
	Объединил сюда аналогичные тесты для методов get, put, delete для заметок
	 с определением ИД.

	 Здесь тестируются:
	 - ИД несуществующей заметки;
	 - Невалидный ИД;
	 - Запрос заметки не от ее владельца.
	"""
	another_user = await create_user(
		f"example_{random.randrange(10000)}@gmail.com", "qwerty123", "Andrew",
		async_client=async_client, raise_error=True
	)

	another_user_headers = {"Authorization": f"Bearer {another_user['token']}"}

	another_user_note = await create_random_note(headers=another_user_headers,
												 async_client=async_client,
												 json=True, raise_error=True)

	match method:
		case "get":
			response_404 = await async_client.get(
				"/api/v1/notes/132435",
				headers=current_user_headers
			)
			response_invalid_id = await async_client.get(
				"/api/v1/notes/qwerty",
				headers=current_user_headers
			)
			response_permissions_error = await async_client.get(
				f"/api/v1/notes/{another_user_note['id']}",
				headers=current_user_headers
			)
		case "put":
			response_404 = await async_client.put(
				"/api/v1/notes/132435",
				headers=current_user_headers
			)
			response_invalid_id = await async_client.put(
				"/api/v1/notes/qwerty",
				headers=current_user_headers
			)
			response_permissions_error = await async_client.put(
				f"/api/v1/notes/{another_user_note['id']}",
				headers=current_user_headers,
				json=dict(note={})
			)
		case "delete":
			response_404 = await async_client.delete(
				"/api/v1/notes/132435",
				headers=current_user_headers
			)
			response_invalid_id = await async_client.delete(
				"/api/v1/notes/qwerty",
				headers=current_user_headers
			)
			response_permissions_error = await async_client.delete(
				f"/api/v1/notes/{another_user_note['id']}",
				headers=current_user_headers
			)
		case _:
			raise AttributeError

	return response_404, response_invalid_id, response_permissions_error


async def day_ratings_rud_test(
	async_client: AsyncClient,
	method: str,
	current_user_headers: dict,
	current_user_id: int
) -> tuple[Response, ...]:
	"""
	Объединил сюда аналогичные тесты для методов get, put, delete для оценок дня
	 с определением их по ИД пользователя и дате.

	 Здесь тестируются:
	 - Дата несуществующей заметки;
	 - Невалидная дата;
	 - Невалидный ИД пользователя;
	 - Запрос оценки дня не от ее создателя.
	"""
	another_user = await create_user(
		f"example_{random.randrange(10_000)}@gmail.com", "qwerty123", "Andrew",
		async_client=async_client, raise_error=True
	)

	another_user_headers = {"Authorization": f"Bearer {another_user['token']}"}

	another_user_day_rating = await create_random_day_rating(headers=another_user_headers,
												 async_client=async_client,
												 json=True, raise_error=True)
	dr_date = another_user_day_rating.get("date")

	match method:
		case "get":
			response_404 = await async_client.get(
				f"/api/v1/day_ratings/user/{current_user_id}?date=2050-01-01",
				headers=current_user_headers
			)
			response_invalid_user_id = await async_client.get(
				f"/api/v1/day_ratings/user/qwerty?date={dr_date}",
				headers=current_user_headers
			)
			response_invalid_date = await async_client.get(
				f"/api/v1/day_ratings/user/{current_user_id}?date=qwerty",
				headers=current_user_headers
			)
			response_permissions_error = await async_client.get(
				f"/api/v1/day_ratings/user/{another_user['id']}?date={dr_date}",
				headers=current_user_headers
			)
		case "put":
			response_404 = await async_client.put(
				f"/api/v1/day_ratings/user/{current_user_id}?date=2050-01-01",
				headers=current_user_headers
			)
			response_invalid_user_id = await async_client.put(
				f"/api/v1/day_ratings/user/qwerty?date={dr_date}",
				headers=current_user_headers
			)
			response_invalid_date = await async_client.put(
				f"/api/v1/day_ratings/user/{current_user_id}?date=qwerty",
				headers=current_user_headers
			)
			response_permissions_error = await async_client.put(
				f"/api/v1/day_ratings/user/{another_user['id']}?date={dr_date}",
				headers=current_user_headers,
				json=dict(day_rating={})
			)
		case "delete":
			response_404 = await async_client.delete(
				f"/api/v1/day_ratings/user/{current_user_id}?date=2050-01-01",
				headers=current_user_headers
			)
			response_invalid_user_id = await async_client.delete(
				f"/api/v1/day_ratings/user/qwerty?date={dr_date}",
				headers=current_user_headers
			)
			response_invalid_date = await async_client.delete(
				f"/api/v1/day_ratings/user/{current_user_id}?date=qwerty",
				headers=current_user_headers
			)
			response_permissions_error = await async_client.delete(
				f"/api/v1/day_ratings/user/{another_user['id']}?date={dr_date}",
				headers=current_user_headers
			)
		case _:
			raise AttributeError

	return response_404, response_invalid_user_id, response_invalid_date, response_permissions_error

