from httpx import AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.users import User, users
from sqlalchemy import update
from .funcs import create_user, convert_obj_creating_time
import datetime


@pytest.mark.usefixtures("generate_user_with_token")
class TestUsers:
	"""
	Пользователь уже готов, получается из conftest.generate_user_with_token.

	Доступны параметры self.email, self.password, self.first_name, self.token,
	 self.id, self.headers, self.registered_at, self.dict (= pydantic schema dict).
	"""
	async def read_users(self, async_test_client: AsyncClient, session: AsyncSession):
		"""
		Получение списка пользователей с правами is_staff.
		Пользователь должен находиться в списке пользователей.
		"""

		query = update(User).where(users.c.id == self.id).values(
			is_staff=True
		)
		await session.execute(query)
		await session.commit()

		response = await async_test_client.get(
			"/api/v1/users/",
			headers=self.headers
		)

		assert response.status_code == 200

		users_list: list[dict] = response.json()

		assert any((user["email"] == self.email and user["id"] == self.id
					for user in users_list))

	async def read_users_errors(self, async_test_client: AsyncClient):
		"""
		Получение списка без прав - ответ 403.
		"""
		response = await async_test_client.get(
			"/api/v1/users/",
			headers=self.headers
		)

		assert response.status_code == 403

	async def test_read_users_me(self, async_test_client: AsyncClient):
		"""
		Получение данных пользователя пользователем.
		Дату/время регистрации форматирую в местные (без нужды, но мб как-то можно после применить).
		"""
		response = await async_test_client.get(
			"/api/v1/users/me",
			headers=self.headers
		)

		assert response.status_code == 200

		user_data = response.json()

		assert "registered_at" in user_data

		local_reg_datetime = convert_obj_creating_time(obj_json=user_data, obj_type="user")

		user_data["registered_at"] = local_reg_datetime

		assert user_data == {
			"email": self.email, "first_name": self.first_name,
			"last_name": None, "registered_at": local_reg_datetime,
			"id": self.id, "is_staff": False, "disabled": False
		}

	async def test_update_user(self, async_test_client: AsyncClient):
		"""
		Тест изменения данных пользователя.
		Is_staff поле изменить нельзя - не должно измениться.
		"""
		updated_data = dict(user={
			"last_name": "Ivanov",
			"is_staff": True
		})

		response = await async_test_client.put(
			f"/api/v1/users/{self.id}",
			json=updated_data,
			headers=self.headers
		)

		assert response.status_code == 200

		updated_user = response.json()

		assert updated_user.get("last_name") == "Ivanov"
		assert updated_user.get("is_staff") is False

	async def test_update_user_errors(self, async_test_client: AsyncClient):
		"""
		Проверка на:
		- Несуществующий ИД;
		- Невалидные данные обновления;
		- Невалидный токен.
		"""
		non_existing_user_response = await async_test_client.put(
			"/api/v1/users/123321",
			headers=self.headers
		)
		assert non_existing_user_response.status_code == 404

		bad_updated_user_data = dict(user={
			"disabled": "yes",
			"password": 1
		})

		bad_updated_user_data_response = await async_test_client.put(
			f"api/v1/users/{self.id}",
			headers=self.headers,
			json=bad_updated_user_data
		)

		assert bad_updated_user_data_response.status_code == 422

	async def test_delete_user(self, async_test_client: AsyncClient):
		"""
		Удаление пользователя.
		"""
		response = await async_test_client.delete(
			f"/api/v1/users/{self.id}",
			headers=self.headers
		)

		assert response.status_code == 200

		assert response.json() == {
			"deleted_user_id": self.id
		}

	async def test_delete_user_errors(self, async_test_client: AsyncClient):
		"""
		Нельзя удалить несуществующего пользователя.
		Нельзя удалить пользователя другому пользователю (если он не is_staff).
		"""
		non_existing_user_response = await async_test_client.delete(
			"/api/v1/users/123321",
			headers=self.headers
		)

		assert non_existing_user_response.status_code == 404

		another_user = await create_user(
			email="andrew@example.com", password="qwerty123",
			firstname="andrew", async_client=async_test_client
		)

		another_user_headers = {
			"Authorization": f"Bearer {another_user['token']}"
		}

		non_permissions_response = await async_test_client.delete(
			f"/api/v1/users/{self.id}",
			headers=another_user_headers
		)

		assert non_permissions_response.status_code == 403
