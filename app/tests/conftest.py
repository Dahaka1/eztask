"""
pytest config
"""
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL_TEST
from sqlalchemy.pool import NullPool
from ..database import Base
from ..models.users import User
from ..models.day_ratings import DayRating
from ..models.notes import Note  # import models for Base metadata updating
import pytest
from fastapi.testclient import TestClient  # = httpx test client
from ..main import app
from typing import AsyncGenerator
import asyncio


engine_test = create_async_engine(DATABASE_URL_TEST, NullPool)
async_session_maker = sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)
Base.metadata.bind = engine_test


@pytest.fixture(autouse=True, scope='session')
async def prepare_database():
	async with engine_test.begin() as conn:
		await conn.run_sync(Base.metadata.create_all)
	yield
	async with engine_test.begin() as conn:
		await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope='session')
def event_loop(request):
	loop = asyncio.get_event_loop_policy().new_event_loop()
	yield loop
	loop.close()


test_client = TestClient(app)


@pytest.fixture(scope='session')
async def async_test_client() -> AsyncGenerator[AsyncClient, None]:
	async with AsyncClient(app=app, base_url="http://test") as ac:
		yield ac
