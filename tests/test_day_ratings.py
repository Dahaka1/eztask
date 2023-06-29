import datetime

import pytest
from httpx import AsyncClient
from .additional.fills import create_random_day_rating, create_random_day_ratings
from .additional.funcs import change_user_params, delete_day_rating
from .additional.subtests import day_ratings_rud_test
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.day_ratings import DayRating
from app.utils import sa_object_to_dict


@pytest.mark.usefixtures("generate_user_with_token")
class TestDayRating:
	async def test_create_day_rating(self, async_test_client: AsyncClient):
		"""
		Создание оценки дня.
		"""
		creating_response = await async_test_client.post(
			"/api/v1/day_ratings/",
			headers=self.headers,
			json=dict(day_rating={"mood": True})
		)
		assert creating_response.status_code == 201
		assert creating_response.json() == {
			"user_id": self.id, "mood": True, "notes": None, "health": None,
			"next_day_expectations": None, "date": datetime.date.today().isoformat()
		}

	async def test_create_day_rating_errors(self, async_test_client: AsyncClient):
		"""
		- Нельзя не передать ни одного параметра оценки дня в json;
		- Нельзя создать больше одной оценки дня для одной даты;
		- Нельзя передать невалидные данные оценки дня.
		"""
		not_any_params_creating_response = await async_test_client.post(
			"/api/v1/day_ratings/",
			headers=self.headers,
			json=dict(day_rating={})
		)

		assert not_any_params_creating_response.status_code == 400

		existing_day_rating = await create_random_day_rating(
			headers=self.headers, async_client=async_test_client, raise_error=True, json=True
		)

		repeated_day_rating = await create_random_day_rating(
			headers=self.headers, async_client=async_test_client, raise_error=False
		)

		assert repeated_day_rating.status_code == 409

		await delete_day_rating(user_id=self.id, date=existing_day_rating["date"],
								headers=self.headers, async_client=async_test_client, raise_error=True)

		invalid_day_rating_data_response = await async_test_client.post(
			"/api/v1/day_ratings/",
			headers=self.headers,
			json=dict(day_rating={"mood": "qwerty"})
		)

		assert invalid_day_rating_data_response.status_code == 422

	async def test_read_day_ratings(self, async_test_client: AsyncClient, session: AsyncSession):
		"""
		Получение is_staff-пользователем списка всех оценок дня.
		"""
		await change_user_params(user_id=self.id, sa_session=session,
								 is_staff=True)

		day_ratings_response_before = await async_test_client.get(
			"/api/v1/day_ratings/",
			headers=self.headers
		)

		assert day_ratings_response_before.status_code == 200

		day_ratings_amount_before = len(day_ratings_response_before.json())
		testing_day_ratings_amount = 5

		await create_random_day_ratings(async_client=async_test_client, amount=testing_day_ratings_amount)

		day_ratings_response_after = await async_test_client.get(
			"/api/v1/day_ratings/",
			headers=self.headers
		)

		assert day_ratings_response_after.status_code == 200
		assert len(day_ratings_response_after.json()) == day_ratings_amount_before + testing_day_ratings_amount

	async def test_read_day_ratings_errors(self, async_test_client: AsyncClient):
		"""
		Только is_staff-пользователь может получить список всех оценок дня.
		"""
		non_permissions_response = await async_test_client.get(
			"/api/v1/day_ratings/",
			headers=self.headers
		)
		assert non_permissions_response.status_code == 403

	async def test_read_day_ratings_me(self, async_test_client: AsyncClient, session: AsyncSession):
		"""
		Получение пользователем списка всех своих оценок дня.
		С опциональной фильтрацией, в том числе.
		"""
		day_rating_response = await create_random_day_rating(headers=self.headers,
															 async_client=async_test_client,
															 raise_error=True,
															 json=True)
		day_ratings_me_response = await async_test_client.get(
			"/api/v1/day_ratings/me",
			headers=self.headers
		)

		assert day_ratings_me_response.status_code == 200
		assert day_ratings_me_response.json() == [day_rating_response]

		await create_random_day_ratings(
			async_client=async_test_client,
			unique_user=True,
			user_id=self.id,
			sa_session=session,
			past_dates=True
		)

		filtered_by_filled_mood_field_day_ratings_response = await async_test_client.get(
			"/api/v1/day_ratings/me?mood=true",
			headers=self.headers
		)

		assert filtered_by_filled_mood_field_day_ratings_response.status_code == 200
		assert all((day_rating["mood"] is not None for day_rating
					in filtered_by_filled_mood_field_day_ratings_response.json()))

		filtered_by_filled_all_fields_day_ratings_response = await async_test_client.get(
			"/api/v1/day_ratings/me?mood=true&health=true&"
			"next_day_expectations=true&notes=true",
			headers=self.headers
		)

		assert filtered_by_filled_all_fields_day_ratings_response.status_code == 200
		assert all((day_rating.values() is not None for day_rating
					in filtered_by_filled_all_fields_day_ratings_response.json()))

	async def test_read_day_ratings_me_errors(self, async_test_client: AsyncClient):
		"""
		- Нельзя передать невалидные параметры запроса (фильтрации оценок дня).
		"""
		invalid_day_ratings_me_response = await async_test_client.get(
			"/api/v1/day_ratings/me?mood=qwerty",
			headers=self.headers
		)

		assert invalid_day_ratings_me_response.status_code == 422

	async def test_update_day_rating(self, async_test_client: AsyncClient, session: AsyncSession):
		"""
		Обновление оценки дня пользователем.
		"""
		day_rating = await create_random_day_rating(headers=self.headers,
											  async_client=async_test_client,
											  raise_error=True,
											  json=True)
		updating_response = await async_test_client.put(
			f"/api/v1/day_ratings/user/{self.id}?date={day_rating['date']}",
			headers=self.headers,
			json=dict(day_rating={"health": False,
								  "mood": True,
								  "notes": True})
		)

		assert updating_response.status_code == 200

		updated_day_rating = await DayRating.get_day_rating(
			user_id=self.id, date=datetime.date.fromisoformat(day_rating["date"]), db=session
		)

		assert updated_day_rating is not None
		updated_day_rating = sa_object_to_dict(updated_day_rating)  # можно и не преобразовывать в словарь, конечно
		assert updated_day_rating["health"] is False
		assert updated_day_rating["mood"] is True
		assert updated_day_rating["notes"] is True

	async def test_update_day_rating_errors(self, async_test_client: AsyncClient):
		"""
		- Нельзя не передать хотя бы один параметр оценки дня.
		- См. 'Day_ratings_rud_test'
		"""
		response_404, response_invalid_user_id, \
			response_invalid_date, response_permissions_error = await day_ratings_rud_test(
				method="put",
				async_client=async_test_client,
				current_user_headers=self.headers,
				current_user_id=self.id
			)
		assert response_404.status_code == 404
		assert response_invalid_user_id.status_code == 422
		assert response_invalid_date.status_code == 422
		assert response_permissions_error.status_code == 403

		day_rating = await create_random_day_rating(
			headers=self.headers, async_client=async_test_client, raise_error=True, json=True
		)

		not_any_params_updating_response = await async_test_client.put(
			f"/api/v1/day_ratings/user/{self.id}?date={day_rating['date']}",
			headers=self.headers,
			json=dict(day_rating={})
		)
		assert not_any_params_updating_response.status_code == 400

	async def test_read_day_rating(self, async_test_client: AsyncClient):
		"""
		Получение оценки дня пользователем.
		"""
		day_rating = await create_random_day_rating(headers=self.headers,
											  async_client=async_test_client,
											  raise_error=True,
											  json=True)
		read_response = await async_test_client.get(
			f"/api/v1/day_ratings/user/{self.id}?date={day_rating['date']}",
			headers=self.headers
		)
		assert read_response.status_code == 200
		assert read_response.json() == day_rating

	async def test_read_day_rating_errors(self, async_test_client: AsyncClient):
		"""
		См. 'Day_ratings_rud_test'.
		"""
		response_404, response_invalid_user_id, \
			response_invalid_date, response_permissions_error = await day_ratings_rud_test(
				method="get",
				async_client=async_test_client,
				current_user_headers=self.headers,
				current_user_id=self.id
			)
		assert response_404.status_code == 404
		assert response_invalid_user_id.status_code == 422
		assert response_invalid_date.status_code == 422
		assert response_permissions_error.status_code == 403

	async def test_delete_day_rating(self, async_test_client: AsyncClient, session: AsyncSession):
		"""
		Удаление оценки дня пользователем.
		"""
		day_rating = await create_random_day_rating(headers=self.headers,
													async_client=async_test_client,
													raise_error=True,
													json=True)
		read_response = await async_test_client.delete(
			f"/api/v1/day_ratings/user/{self.id}?date={day_rating['date']}",
			headers=self.headers
		)
		assert read_response.status_code == 200

		deleted_day_rating = await DayRating.get_day_rating(user_id=self.id,
													  db=session,
													  date=datetime.date.fromisoformat(day_rating["date"]))
		assert deleted_day_rating is None

	async def test_delete_day_rating_errors(self, async_test_client: AsyncClient):
		"""
		См. 'Day_ratings_rud_test'.
		"""
		response_404, response_invalid_user_id, \
			response_invalid_date, response_permissions_error = await day_ratings_rud_test(
				method="delete",
				async_client=async_test_client,
				current_user_headers=self.headers,
				current_user_id=self.id
			)
		assert response_404.status_code == 404
		assert response_invalid_user_id.status_code == 422
		assert response_invalid_date.status_code == 422
		assert response_permissions_error.status_code == 403
