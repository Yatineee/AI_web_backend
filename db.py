from sqlmodel import create_engine, Session, SQLModel
from models.session import SessionLog

sqlite_url = "sqlite:///./sessions.db"
engine = create_engine(sqlite_url, echo=False)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)
