import os

from passlib.context import CryptContext

DB_PARAMS = {"user": os.environ.get("DB_USER"), "password": os.environ.get("DB_PASSWORD"),
	"host": os.environ.get("DB_HOST"), "port": os.environ.get("DB_PORT"), "dbname": os.environ.get("DB_NAME")}

DB_PARAMS_TEST = {"user": os.environ.get("DB_USER_TEST"), "password": os.environ.get("DB_PASSWORD_TEST"),
	"host": os.environ.get("DB_HOST_TEST"), "port": os.environ.get("DB_PORT_TEST"),
				  "dbname": os.environ.get("DB_NAME_TEST")}


DATABASE_URL = "postgresql+asyncpg://%s:%s@%s:%s/%s" % tuple(DB_PARAMS.values())

DATABASE_URL_TEST = "postgresql+asyncpg://%s:%s@%s:%s/%s" % tuple(DB_PARAMS_TEST.values())


API_DOCS_URL = "/api/v1/docs"
OPENAPI_URL = "/api/v1/openapi.json"

# loguru logger settings
LOGGING_OUTPUT = "logs.log"
LOGGING_PARAMS = {
	"sink": LOGGING_OUTPUT,
	"rotation": "1 MB",
	"compression": "zip"
}

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
