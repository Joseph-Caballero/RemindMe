import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True)

class Base(DeclarativeBase):
    pass

SessionLocal = sessionmaker(
    bind = engine,
    autoflush = False,
    autocommit = False
)

def init_db():
    from app.models import Reminder
    Base.metadata.create_all(bind = engine)