from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER


class Base(DeclarativeBase):
    pass


engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
