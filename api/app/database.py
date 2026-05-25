from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


def make_engine(url: str):
    return create_async_engine(url, echo=False)


def make_session_factory(engine):
    return async_sessionmaker(engine, expire_on_commit=False)
