import datetime
from httpx import AsyncClient


async def test_register(ac: AsyncClient):
	test_user = {
		"email": "user@gmail.com",
		"password": "qwerty",
		"first_name": "Andrew"
	}
	response = await ac.post(
		"/api/v1/users", json=test_user
	)

	assert response.status_code == 201
	assert response.json() == {
		**test_user,
		"registered_at": datetime.date.today(),
		"disabled": False,
		"is_staff": False,
		"id": 1
	}
