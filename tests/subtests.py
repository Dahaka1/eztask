from httpx import AsyncClient
from .funcs import create_user, create_random_note


async def notes_rud_test(
	async_client: AsyncClient,
	method: str,
	current_user_headers: dict
):
	"""
	Объединил сюда аналогичные тесты для методов get, put, delete для заметок
	 с определением ИД.

	 Здесь тестируются:
	 - ИД несуществующей заметки;
	 - Невалидный ИД;
	 - Запрос заметки не от ее владельца.
	"""
	another_user = await create_user(
		"example@gmail.com", "qwerty123", "Andrew",
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
				headers=current_user_headers
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

	assert response_404.status_code == 404
	assert response_invalid_id.status_code == 422
	assert response_permissions_error.status_code == 403
