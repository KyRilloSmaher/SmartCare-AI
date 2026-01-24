
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from App.config.base import BaseConfig

engine = create_engine(
    BaseConfig.MSSQL_CONNECTION_STRING,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_session():
    return SessionLocal()

