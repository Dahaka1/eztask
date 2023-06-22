from loguru import logger
import config
from .database import sync_db
from .static.sql_queries import GET_ALL_TABLES
import os


def logger_init() -> None:
	"""
	Использую loguru для дополнительного логирования.
	"""
	for level in config.LOGGING_LEVELS:
		logger.add(
			config.ERRORS_OUTPUT_FILE,
			level=level,
			format=config.LOGGING_FORMAT,
			rotation="1 MB",
			compression="zip"
		)


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
