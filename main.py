from dotenv import load_dotenv

load_dotenv()

# importing from app after load dotenv because
# .env params are needed for database initializing
from app import logger_init, database_init, start_app


def main():
	"""
	Synchronous preparing for starting app
	"""
	logger_init()
	database_init()
	start_app()


if __name__ == '__main__':
	main()
