from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from ..dependencies import get_user_id, get_async_session, get_polling_id
from sqlalchemy.ext.asyncio import AsyncSession
from ..crud.crud_polling import get_user_polling, update_user_polling


router = APIRouter(
	prefix="/polling",
	tags=["user_polling"]
)


@router.get("/user/{user_id}")
async def get_polling(
	user_id: Annotated[int, Depends(get_user_id)],
	db: Annotated[AsyncSession, Depends(get_async_session)]
):
	"""
	Получение опроса для пользователя на сегодняшний день.

	Если нет - код 404.
	"""
	polling = await get_user_polling(user_id=user_id, db=db)
	if polling:
		return polling
	raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Polling not found")


@router.put("/{polling_id}")
async def update_polling(
	polling_id: Annotated[int, Depends(get_polling_id)],
	db: Annotated[AsyncSession, Depends(get_async_session)]
):
	"""
	Обновление статуса опроса.

	Передавать ничего не надо - автоматически обновляется статус (completed=True).

	Обновляется после того, как опрос осуществился.
	"""
	await update_user_polling(polling_id=polling_id, db=db)

	return {"completed": polling_id}
