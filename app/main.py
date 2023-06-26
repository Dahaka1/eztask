from fastapi import FastAPI, APIRouter
from .database import db
from .routers import users, auth, notes, day_ratings
import config
from loguru import logger


app = FastAPI(
	openapi_url=config.OPENAPI_URL,
	docs_url=config.API_DOCS_URL,
	redoc_url=None
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(users.router)
api_router.include_router(auth.router)
api_router.include_router(notes.router)
api_router.include_router(day_ratings.router)

app.include_router(api_router)


@app.on_event("startup")
async def startup():
	"""
	Действия при старте сервера.
	"""
	logger.add("logs.log")
	logger.info("Starting server")
	await db.connect()


@app.on_event("shutdown")
async def shutdown():
	"""
	Действия при отключении сервера.
	"""
	logger.info("Stopping server")
	await db.disconnect()



