"""Database initialization."""
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from droos_bot import PARENT_DIR
from droos_bot.db.base import Base

db_connection_string = f"sqlite:///{PARENT_DIR}/droos_bot.db"
engine = create_engine(db_connection_string, connect_args={"check_same_thread": False})

Base.metadata.create_all(bind=engine)

session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
