import pytest
from httpx import AsyncClient
import datetime
from app.static.enums import PollingTypeEnum
from app.models.polling import PollingString
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio


@pytest.mark.usefixtures("generate_user_with_token")
class TestPolling:
	async def test_polling_creating(self, async_test_client: AsyncClient, session: AsyncSession):
		"""
		При любом действии от пользователя создается случайный опрос
		 для текущего дня, если еще не был создан.
		"""
		user_action = await async_test_client.get(
			"/api/v1/notes/me",
			headers=self.headers
		)
		assert user_action.status_code == 200

		await asyncio.sleep(3)  # бэкграунд-задачи не успевают сразу сделать опрос

		user_polling = await async_test_client.get(
			f"/api/v1/polling/user/{self.id}"
		)

		assert user_polling.status_code == 200

		polling_data = user_polling.json()
		poll_type = polling_data["poll_type"]

		assert polling_data["created_at"] == datetime.date.today().isoformat()
		assert poll_type in PollingTypeEnum._member_map_.keys()
		assert polling_data["user_id"] == self.id

		polls = await PollingString.get_polling_type_strings(
			polling_type=poll_type, db=session
		)

		assert polling_data["polling_string_id"] in [
			poll["id"] for poll in polls
		]

		assert polling_data["completed"] is False

	async def test_polling_creating_when_user_delete_self(self, async_test_client: AsyncClient):
		"""
		Если действие пользователя - удаление профиля, то опрос
		 не создается.
		"""
		user_deleting = await async_test_client.delete(
			f"/api/v1/users/{self.id}",
			headers=self.headers
		)

		assert user_deleting.status_code == 200

		user_polling = await async_test_client.get(
			f"/api/v1/polling/user/{self.id}"
		)

		assert user_polling.status_code == 404

	async def test_update_polling(self, async_test_client: AsyncClient):
		"""
		Обновление опроса пользователя.
		"""
		user_action = await async_test_client.get(
			f"/api/v1/notes/me",
			headers=self.headers
		)

		assert user_action.status_code == 200

		await asyncio.sleep(3)  # бэкграунд-задачи не успевают сразу сделать опрос

		user_polling = await async_test_client.get(
			f"/api/v1/polling/user/{self.id}"
		)

		assert user_polling.status_code == 200

		polling_id = user_polling.json().get("id")

		updated_polling = await async_test_client.put(
			f"/api/v1/polling/{polling_id}"
		)

		assert updated_polling.status_code == 200

		updated_user_polling = await async_test_client.get(
			f"/api/v1/polling/user/{self.id}"
		)

		updated_user_polling_data = updated_user_polling.json()

		assert updated_user_polling_data["completed"] is True
		assert datetime.datetime.fromisoformat(updated_user_polling_data["completed_at"]).date() == \
			   datetime.date.today()

	async def test_update_polling_errors(self, async_test_client: AsyncClient):
		"""
		- Нельзя обновить несуществующий опрос.
		"""
		updated_non_existing_polling = await async_test_client.put(
			f"/api/v1/polling/132435"
		)
		assert updated_non_existing_polling.status_code == 404
