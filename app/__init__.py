import os

from loguru import logger

import config
from .database import sync_db
from .static.sql_queries import GET_ALL_TABLES
from .models.polling import PollingString
from .crud.crud_polling import create_polling_strings

from redis import asyncio as aioredis, ConnectionError
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from sqlalchemy.orm import sessionmaker


def database_init() -> None:
	"""
	Создание таблиц в БД по умолчанию.
	"""
	with sync_db.cursor() as cursor:
		cursor.execute(GET_ALL_TABLES)
		all_tables = cursor.fetchall()
	if not sync_db.closed:
		sync_db.close()
	if not any(all_tables) or config.DB_AUTO_UPDATING is True:
		for cmd in config.ALEMBIC_MIGRATION_CMDS:
			os.system(cmd)
		logger.info(f"There are default DB tables was successfully created")


def start_app() -> None:
	"""
	Запуск сервера.
	"""
	os.system(config.STARTING_APP_CMD)


async def fastapi_cache_init() -> None:
	"""
	Используется при старте сервера, а также при начале тестирования.
	Redis должен быть активен!
	"""
	await check_redis_connection()
	redis = aioredis.from_url(config.REDIS_URL)
	FastAPICache.init(RedisBackend(redis), prefix=config.REDIS_CACHE_PREFIX)


async def check_redis_connection() -> None:
	"""
	Redis при инициализации кэширования может и не быть активным - при этом нет ошибки.
	Делаю доп. проверку.
	"""
	r = await aioredis.from_url(config.REDIS_URL)
	try:
		await r.ping()
	except ConnectionError:
		logger.error("Can't establish a connection to Redis")
		exit(0)
	finally:
		await r.close()


async def init_db_strings(sa_session_maker: sessionmaker) -> None:
	"""
	Здесь создаются статические данные по умолчанию, которые нужно создать при запуске сервера,
	 если их еще нет.

	Sa_session_maker передаю извне, ибо в тестах и в приложении они отличаются.
	"""
	async with sa_session_maker() as session:  # делать еще одну БД-сессию, конечно, не надо,
		# но другого варианта получить ее здесь я не нашел(
		await create_polling_strings(db=session)
