from fastapi import FastAPI, APIRouter, status
from fastapi.responses import RedirectResponse
from loguru import logger

import config
from config import LOGGING_PARAMS
from .routers import users, auth, notes, day_ratings, polling
from . import fastapi_cache_init, init_db_strings, check_connections
from .database import async_session_maker
from .static import app_description


app = FastAPI(
	title="EZTask",
	openapi_url=config.OPENAPI_URL,
	docs_url=config.API_DOCS_URL,
	redoc_url=None,
	description=app_description(),
	summary="Note your life easy!",
	version="0.0.1",
	contact={
		"name": "Yaroslav",
		"email": "ijoech@gmail.com"
	}

)

api_router = APIRouter(prefix="/api/v1")
for r in (users, auth, notes, day_ratings, polling):
	api_router.include_router(r.router)

app.include_router(api_router)


@app.on_event("startup")
async def startup():
	"""
	Действия при старте сервера.
	"""
	logger.add(**LOGGING_PARAMS)
	logger.info("Starting server")
	await check_connections()
	await fastapi_cache_init()
	await init_db_strings(async_session_maker)


@app.on_event("shutdown")
async def shutdown():
	"""
	Действия при отключении сервера.
	"""
	logger.info("Stopping server")


@app.get("/docs")
async def docs():
	return RedirectResponse(
		url="/api/v1/docs",
		status_code=status.HTTP_308_PERMANENT_REDIRECT
	)
