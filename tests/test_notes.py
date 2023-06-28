import pytest
from httpx import AsyncClient
import datetime
from .funcs import create_random_note, change_user_params, create_user, convert_obj_creating_time, \
	convert_creating_time_for_objects_list
from sqlalchemy.ext.asyncio import AsyncSession
from app.static import enums


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
			date=datetime.date.today() - datetime.timedelta(days=1)
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

		Дату и время создания конвертирую.
		"""

		note_1 = await create_random_note(headers=self.headers, async_client=async_test_client, json=True)
		note_2 = await create_random_note(note_type="task", headers=self.headers,
										  async_client=async_test_client, json=True)

		notes_list = [note_1, note_2]

		user_notes_response = await async_test_client.get(
			"/api/v1/notes/me",
			headers=self.headers
		)

		user_notes = user_notes_response.json()

		assert isinstance(user_notes, list)
		assert len(user_notes) == 2
		assert all((note["created_at"] is not None for note in user_notes))

		notes_list, user_notes = convert_creating_time_for_objects_list(notes_list, user_notes, obj_type="note")

		assert user_notes == notes_list

	async def test_read_notes_me_with_filtering_and_sorting(self, async_test_client: AsyncClient):
		"""
		Фильтрация и сортировка списка заметок.
		Параметры: sorting, period, type, completed.

		Варианты параметров - в schemas.GetNotesParams
		"""

		note_1 = await create_random_note(headers=self.headers, async_client=async_test_client, json=True)
		note_2 = await create_random_note(note_type="task", headers=self.headers,
										  async_client=async_test_client,
										  date=datetime.date.today() + datetime.timedelta(days=10), json=True)

		notes_list = [note_1, note_2]

		sorting_date_desc = enums.NotesOrderByEnum.date_desc.value

		sorted_by_date_desc_notes_response = await async_test_client.get(
			f"/api/v1/notes/me?sorting={sorting_date_desc}", headers=self.headers
		)

		assert sorted_by_date_desc_notes_response.status_code == 200

		sorted_by_date_desc_notes = sorted_by_date_desc_notes_response.json()

		notes_list, sorted_by_date_desc_notes = convert_creating_time_for_objects_list(
			notes_list, sorted_by_date_desc_notes, obj_type="note"
		)

		assert sorted_by_date_desc_notes_response.json() == sorted(notes_list,
																   key=lambda note: note["created_at"], reverse=True)

	async def test_read_note(self, async_test_client: AsyncClient):
		"""
		Чтение заметки пользователем.
		"""
		note = await create_random_note(headers=self.headers, async_client=async_test_client, json=True)
		note["created_at"] = datetime.datetime.fromisoformat(note["created_at"])

		response = await async_test_client.get(
			f"/api/v1/notes/{note['id']}",
			headers=self.headers
		)

		created_note_data = response.json()

		assert isinstance(created_note_data, dict)
		assert "created_at" in created_note_data and created_note_data["created_at"] is not None

		readed_note_creating_datetime = convert_obj_creating_time(obj_json=created_note_data, obj_type="note")

		created_note_data["created_at"] = readed_note_creating_datetime
		assert created_note_data == note

	async def test_read_note_errors(self, async_test_client: AsyncClient):
		pass
