from dotenv import load_dotenv

load_dotenv()

# importing from app after load dotenv because
# .env params are needed for database initializing
from app import database_init, start_app
from loguru import logger
from config import LOGGING_PARAMS


def main():
	"""
	Synchronously preparing for starting app
	"""
	logger.add(**LOGGING_PARAMS)
	database_init()
	start_app()


if __name__ == '__main__':
	main()
