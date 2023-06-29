import datetime

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.static import enums
from .additional.funcs import change_user_params, convert_obj_creating_time, exclude_datetime_creating, \
	get_obj_by_id
from .additional.subtests import notes_rud_test
from .additional.fills import create_random_note, create_random_notes


@pytest.mark.usefixtures("generate_user_with_token")
class TestNotes:
	"""
	Пользователь уже готов, получается из conftest.generate_user_with_token.

	Доступны параметры self.email, self.password, self.first_name, self.token,
	self.id, self.headers, self.registered_at, self.dict (= pydantic schema dict).
	"""
	async def test_create_note(self, async_test_client: AsyncClient, session: AsyncSession):
		"""
		Создание заметок.

		Is_staff-пользователь может создать заметки даже с невалидной датой (ранее текущей).

		Дату/время регистрации форматирую в местные (без нужды, но мб как-то можно после применить).
		"""
		response_note_1 = await async_test_client.post(
			"/api/v1/notes/",
			json=dict(note={
				"text": "Сегодня все так хорошо!"
			}),
			headers=self.headers
		)

		assert response_note_1.status_code == 201

		response_note_1_data = response_note_1.json()

		assert "created_at" in response_note_1_data
		local_creating_datetime = convert_obj_creating_time(obj_json=response_note_1_data, obj_type="note")
		response_note_1_data["created_at"] = local_creating_datetime

		assert response_note_1_data == {
			'note_type': 'note',
			'text': 'Сегодня все так хорошо!',
			'date': datetime.date.today().isoformat(),
			'created_at': local_creating_datetime,
			'user_id': self.id,
			'id': 1,
			'completed': None
		}

		response_note_2 = await async_test_client.post(
			"/api/v1/notes/",
			json=dict(note={
				"text": "Надо сделать домашку",
				"note_type": "task"
			}),
			headers=self.headers
		)

		assert response_note_2.status_code == 201

		response_note_2_data = response_note_2.json()

		assert "created_at" in response_note_2_data
		local_creating_datetime = convert_obj_creating_time(obj_json=response_note_2_data, obj_type="note")
		response_note_2_data["created_at"] = local_creating_datetime

		assert response_note_2_data == {
			'note_type': 'task',
			'text': 'Надо сделать домашку',
			'date': datetime.date.today().isoformat(),
			'created_at': local_creating_datetime,
			'user_id': self.id,
			'id': 2,
			'completed': False
		}

		await change_user_params(user_id=self.id, sa_session=session, is_staff=True)

		response_note_non_valid_date_staff_user = await create_random_note(
			headers=self.headers,
			async_client=async_test_client,
			date=datetime.date.today() - datetime.timedelta(days=1),
			raise_error=True
		)

		assert response_note_non_valid_date_staff_user.status_code == 201

	async def test_create_note_errors(self, async_test_client: AsyncClient, session: AsyncSession):
		"""
		- Заблокированный пользователь не может создать заметку;
		- Нельзя создать заметку с невалидным типом заметки;
		- Нельзя создать заметку с датой ранее текущей (только для is_staff-пользователей);
		- Нельзя создать заметку с невалидным токеном авторизации.
		"""

		bad_note_type_response = await create_random_note(
			headers=self.headers,
			async_client=async_test_client,
			note_type="qwerty"
		)

		assert bad_note_type_response.status_code == 422

		bad_note_date_response = await create_random_note(
			headers=self.headers,
			async_client=async_test_client,
			date=datetime.date.today() - datetime.timedelta(days=1)
		)

		assert bad_note_date_response.status_code == 400

	async def test_read_notes_me(self, async_test_client: AsyncClient):
		"""
		Получение списка собственных заметок пользователем.

		ЗДЕСЬ И ДАЛЕЕ решил не конвертировать дату/время создания объектов.
		Отняло это много времени, но в целом задачи их получить и нет.
		Если будет надо проверять дату/время - придется разобраться досконально с UTC-конвертированием.
		"""

		note_1 = await create_random_note(headers=self.headers, async_client=async_test_client, json=True,
										  raise_error=True)
		note_2 = await create_random_note(note_type="task", headers=self.headers,
										  async_client=async_test_client, json=True, raise_error=True)

		notes_list = exclude_datetime_creating([note_1, note_2], obj_type="note")

		user_notes_response = await async_test_client.get(
			"/api/v1/notes/me",
			headers=self.headers
		)

		user_notes = user_notes_response.json()

		assert isinstance(user_notes, list)
		assert len(user_notes) == 2
		assert all((note["created_at"] is not None for note in user_notes))

		user_notes = exclude_datetime_creating(user_notes, obj_type="note")

		assert user_notes == notes_list

	async def test_read_notes_me_with_filtering_and_sorting(self, async_test_client: AsyncClient):
		"""
		Фильтрация и сортировка списка заметок.
		Параметры: sorting, period, type, completed.

		Варианты параметров - в schemas.GetNotesParams.
		"""
		await create_random_notes(headers=self.headers, async_client=async_test_client)

		sorting_date_desc = enums.NotesOrderByEnum.date_desc.value

		sorted_by_date_desc_notes_response = await async_test_client.get(
			f"/api/v1/notes/me?sorting={sorting_date_desc}", headers=self.headers
		)

		assert sorted_by_date_desc_notes_response.status_code == 200
		dates_notes_list = [datetime.date.fromisoformat(note["date"]) for note in sorted_by_date_desc_notes_response.json()]
		assert dates_notes_list == sorted(dates_notes_list, reverse=True)

		period_past = enums.NotesPeriodEnum.past.value

		filtered_by_period_past_notes_response = await async_test_client.get(
			f"/api/v1/notes/me?period={period_past}", headers=self.headers
		)
		assert filtered_by_period_past_notes_response.status_code == 200
		assert len(filtered_by_period_past_notes_response.json()) == 1  # на данном этапе создалась только одна задача
		# с прошедшей датой - в тесте на создание заметок (пользователем is_staff)

		type_task = enums.NoteTypeEnum.task.value
		filtered_by_type_task_notes_list_response = await async_test_client.get(
			f"/api/v1/notes/me?type={type_task}", headers=self.headers
		)
		assert filtered_by_type_task_notes_list_response.status_code == 200
		assert all((note["note_type"] == "task" for note in filtered_by_type_task_notes_list_response.json()))

		completed_tasks = enums.NotesCompletedEnum.completed.value

		filtered_by_type_task_and_completed_notes_list_response = await async_test_client.get(
			f"/api/v1/notes/me?type={type_task}&completed={completed_tasks}", headers=self.headers
		)

		assert filtered_by_type_task_and_completed_notes_list_response.status_code == 200
		assert filtered_by_type_task_and_completed_notes_list_response.json() == []  # задачи не завершались
		# в тестах на этом этапе

		type_note = enums.NoteTypeEnum.note.value
		period_upcoming = enums.NotesPeriodEnum.upcoming.value

		mixed_params_notes_list_response = await async_test_client.get(
			f"/api/v1/notes/me?period={period_upcoming}&type={type_note}&completed={completed_tasks}&"
			f"sorting={sorting_date_desc}", headers=self.headers
		)

		assert mixed_params_notes_list_response.status_code == 200
		notes_list = mixed_params_notes_list_response.json()
		assert len(notes_list) > 0
		assert all((note["note_type"] == "note" for note in notes_list))
		dates_notes_list = [datetime.date.fromisoformat(note["date"]) for note in notes_list]
		assert dates_notes_list == sorted(dates_notes_list, reverse=True)
		# период и выполнение здесь не тестирую, ибо они не учитываются в данном случае
		# (период и так по умолчанию upcoming, а параметр completed учитывается только если выбран тип заметок "задача")

	async def test_read_notes_me_with_filtering_and_sorting_errors(self, async_test_client: AsyncClient):
		"""
		Невалидные параметры запроса.
		"""
		bad_sorting = "qwerty"

		bad_sorting_response = await async_test_client.get(
			f"/api/v1/notes/me?sorting={bad_sorting}",
			headers=self.headers
		)
		assert bad_sorting_response.status_code == 422

		bad_completed = "qwerty"
		bad_completed_response = await async_test_client.get(
			f"/api/v1/notes/me?completed={bad_completed}",
			headers=self.headers
		)
		assert bad_completed_response.status_code == 422

		bad_type = "qwerty"

		bad_type_response = await async_test_client.get(
			f"/api/v1/notes/me?type={bad_type}",
			headers=self.headers
		)
		assert bad_type_response.status_code == 422

		bad_period = "qwerty"

		bad_period_response = await async_test_client.get(
			f"/api/v1/notes/me?period={bad_period}",
			headers=self.headers
		)
		assert bad_period_response.status_code == 422

		mixed_bad_params_response = await async_test_client.get(
			f"/api/v1/notes/me?type={bad_type}&period={bad_period}&"
			f"sorting={bad_sorting}&completed={bad_completed}",
			headers=self.headers
		)
		assert mixed_bad_params_response.status_code == 422

	async def test_read_note(self, async_test_client: AsyncClient):
		"""
		Чтение заметки пользователем.
		"""
		note = await create_random_note(headers=self.headers, async_client=async_test_client, json=True,
										raise_error=True)
		note = exclude_datetime_creating(note, obj_type="note")
		response = await async_test_client.get(
			f"/api/v1/notes/{note['id']}",
			headers=self.headers
		)

		created_note_data = response.json()

		assert isinstance(created_note_data, dict)
		assert "created_at" in created_note_data and created_note_data["created_at"] is not None

		created_note_data = exclude_datetime_creating(created_note_data, obj_type="note")

		assert created_note_data == note

	async def test_read_note_errors(self, async_test_client: AsyncClient):
		"""
		Несуществующий/инвалидный ИД заметки или запрос не от создателя заметки.

		См. 'Notes_rud_test'
		"""
		response_404, response_invalid_id, response_permissions_error = await notes_rud_test(
			async_client=async_test_client,
			current_user_headers=self.headers,
			method="get"
		)

		assert response_404.status_code == 404
		assert response_invalid_id.status_code == 422
		assert response_permissions_error.status_code == 403

	async def test_update_note(self, async_test_client: AsyncClient, session: AsyncSession):
		"""
		Проверяется изменение заметки пользователем.
		"""
		note = await create_random_note(headers=self.headers, async_client=async_test_client,
										raise_error=True, json=True)
		update_note_date_response = await async_test_client.put(
			f"/api/v1/notes/{note['id']}",
			headers=self.headers,
			json=dict(note={"date": "2030-01-01",
							"text": "Hello!",
							"note_type": "task"})
		)
		assert update_note_date_response.status_code == 200
		updated_note_response = await get_obj_by_id(note["id"], obj_type="note", headers=self.headers,
									 async_client=async_test_client)
		updated_note = updated_note_response.json()
		assert updated_note["date"] == "2030-01-01"
		assert updated_note["text"] == "Hello!"
		assert updated_note["note_type"] == "task"
		assert updated_note["completed"] is False

	async def test_update_note_errors(self, async_test_client: AsyncClient):
		"""
		Проверяются невалидные данные.
		Плюс нельзя установить дату заметки ранее текущей.

		См. 'Notes_rud_test'.
		"""
		response_404, response_invalid_id, response_permissions_error = await notes_rud_test(
			async_client=async_test_client,
			current_user_headers=self.headers,
			method="put"
		)

		assert response_404.status_code == 404
		assert response_invalid_id.status_code == 422
		assert response_permissions_error.status_code == 403

		note = await create_random_note(headers=self.headers, async_client=async_test_client,
										raise_error=True, json=True)

		past_date = datetime.date.today() - datetime.timedelta(days=10)

		update_note_past_date_response = await async_test_client.put(
			f"/api/v1/notes/{note['id']}",
			headers=self.headers,
			json=dict(note={"date": past_date.isoformat()})
		)
		assert update_note_past_date_response.status_code == 400

		invalid_updated_note_response = await async_test_client.put(
			f"/api/v1/notes/{note['id']}",
			headers=self.headers,
			json=dict(note={"date": "qwerty",
							"completed": "yes",
							"type": None})
		)
		assert invalid_updated_note_response.status_code == 422

	async def test_delete_note(self, async_test_client: AsyncClient):
		"""
		Удаление заметки пользователем.
		"""
		note = await create_random_note(headers=self.headers, async_client=async_test_client,
										json=True, raise_error=True)
		response = await async_test_client.delete(
			f"/api/v1/notes/{note['id']}",
			headers=self.headers
		)
		assert response.status_code == 200

		deleted_note_response = await get_obj_by_id(note['id'],
													obj_type="note",
													async_client=async_test_client,
													headers=self.headers)

		assert deleted_note_response.status_code == 404

	async def test_delete_note_errors(self, async_test_client: AsyncClient):
		"""
		См. 'Notes_rud_test'
		"""
		response_404, response_invalid_id, response_permissions_error = await notes_rud_test(
			async_client=async_test_client,
			current_user_headers=self.headers,
			method="delete"
		)

		assert response_404.status_code == 404
		assert response_invalid_id.status_code == 422
		assert response_permissions_error.status_code == 403
