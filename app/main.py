from fastapi import FastAPI, APIRouter
from .database import db
from .routers import users, auth


app = FastAPI()

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(users.router)
api_router.include_router(auth.router)

app.include_router(api_router)


@app.on_event("startup")
async def startup():
	"""
	Подключение к БД при запуске сервера.
	"""
	await db.connect()


@app.on_event("shutdown")
async def shutdown():
	"""
	Закрытие подключения при остановке сервера.
	"""
	await db.disconnect()



