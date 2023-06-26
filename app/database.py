from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
import config
import databases
from psycopg2 import connect

SQLALCHEMY_DATABASE_URL = config.DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# db connection instance (async mode)
db = databases.Database(url=config.DATABASE_URL)

# db connection instance (sync mode)
sync_db = connect(
    **config.DB_PARAMS
)

