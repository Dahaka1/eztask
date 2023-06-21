from fastapi import FastAPI
from .database import db


app = FastAPI()


@app.on_event("startup")
async def startup():
	"""
	Подключение к БД при запуске сервера
	"""
	await db.connect()


@app.on_event("shutdown")
async def shutdown():
	"""
	Закрытие подключения при остановке сервера
	"""
	await db.disconnect()

