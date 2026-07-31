from app.database.base import Base
from app.database.connection import engine

# Import every model here
from app.models.chat import Chat


def create_tables():
    """
    Create all database tables.
    This runs automatically when FastAPI starts.
    """
    Base.metadata.create_all(bind=engine)