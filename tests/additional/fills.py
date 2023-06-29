import datetime
import random
from typing import Any

from httpx import AsyncClient, Response
from sqlalchemy import insert
from app.models.day_ratings import DayRating
from sqlalchemy.ext.asyncio import AsyncSession

from .auth import get_user_token


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


async def create_random_day_rating(
	headers: dict,
	async_client: AsyncClient,
	raise_error: bool = False,
	json: bool = False
) -> Response | dict:
	"""
	Создает рандомную оценку дня.
	"""
	bools = (True, False)
	creating_response = await async_client.post(
		"/api/v1/day_ratings/",
		headers=headers,
		json=dict(day_rating={
			"mood": random.choice(bools),
			"next_day_expectations": random.choice(bools),
			"health": random.choice(bools),
			"notes": random.choice(bools)
		})
	)
	if raise_error is True:
		if creating_response.status_code != 201:
			raise AssertionError(f"Can't create a new day rating: server response "
								 f"status code is {creating_response.status_code}")

	return creating_response if json is False else creating_response.json()


async def create_random_day_ratings(
	async_client: AsyncClient,
	amount: int = 10,
	unique_user: bool = False,
	user_id: int = None,
	sa_session: AsyncSession = None,
	past_dates: bool = True
) -> None:
	"""
	Создает переданное количество рандомных оценок дня.
	Может создать их для разных пользователей (по умолчанию).
	А может - для пользователя с переданным ИД. В таком случае можно выбрать установку прошедших дат
	(использую это для теста получения оценок дня с фильтрами) - выбрана по умолчанию.
	"""
	if unique_user is False:
		for _ in range(amount):
			user = await create_user(
				email=random.choice([f"qwerty_{random.randrange(10_000)}@gmail.com" for _ in range(10)]),
				password="qwerty123",
				firstname="Test",
				async_client=async_client,
				raise_error=True
			)
			await create_random_day_rating(headers={"Authorization": f"Bearer {user['token']}"},
										   async_client=async_client,
										   raise_error=True)
	else:
		if user_id is None or sa_session is None:
			raise AttributeError
		bools = (True, False)
		for date_num in range(amount):
			if past_dates is True:
				day_rating_date = datetime.date.today() - datetime.timedelta(days=date_num + 1)
			else:
				day_rating_date = datetime.date.today() + datetime.timedelta(days=date_num + 1)
			query = insert(DayRating).values(
				user_id=user_id,
				date=day_rating_date,
				mood=random.choice(bools),
				health=random.choice(bools),
				next_day_expectations=random.choice(bools),
				notes=random.choice(bools)
			)
			await sa_session.execute(query)
			await sa_session.commit()
