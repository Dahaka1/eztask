import os
from passlib.context import CryptContext


DB_PARAMS = {"user": os.environ.get("DB_USER"), "password": os.environ.get("DB_PASSWORD"),
	"host": os.environ.get("DB_HOST"), "port": os.environ.get("DB_PORT"), "dbname": os.environ.get("DB_NAME")}


DATABASE_URL = "postgresql://%s:%s@%s:%s/%s" % tuple(DB_PARAMS.values())


# loguru logger settings
LOGGING_FORMAT = '{time} {level} {message}'
ERRORS_OUTPUT_FILE = 'logs.log'
LOGGING_LEVELS = [
	"ERROR",
	"INFO"
]


# alembic: commands for initializing migrations
ALEMBIC_MIGRATION_CMDS = [
	"alembic revision --autogenerate",
	"alembic upgrade head"
]
# alembic: if parameter is True, alembic will check models changing in every server launching
# e.g. even if model field attributes was changed, it will automatically reflect in DB
DB_AUTO_UPDATING = False

STARTING_APP_CMD = "uvicorn app.main:app --reload"

# users passwords hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# jwt token params
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
JWT_SIGN_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
