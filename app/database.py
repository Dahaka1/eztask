from sqlalchemy.orm import declarative_base, sessionmaker
import config
from psycopg2 import connect
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

SQLALCHEMY_DATABASE_URL = config.DATABASE_URL

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL
)

async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

# db connection instance (sync mode, using while starting app)
sync_db = connect(
    **config.DB_PARAMS
)
