from dotenv import load_dotenv

load_dotenv()

# importing from app after load dotenv because
# .env params are needed for database initializing
from app import logger_init, database_init, start_app

# TODO: разобраться, почему loguru.logger не пишет логи в файл даже после инициализации


def main():
	"""
	Synchronously preparing for starting app
	"""
	logger_init()
	database_init()
	start_app()


if __name__ == '__main__':
	main()
