from fastapi import FastAPI, APIRouter
from loguru import logger

import config
from config import LOGGING_PARAMS
from .routers import users, auth, notes, day_ratings
from . import fastapi_cache_init, init_db_strings
from .database import async_session_maker


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
	logger.add(**LOGGING_PARAMS)
	logger.info("Starting server")
	await fastapi_cache_init()
	await init_db_strings(async_session_maker)


@app.on_event("shutdown")
async def shutdown():
	"""
	Действия при отключении сервера.
	"""
	logger.info("Stopping server")
