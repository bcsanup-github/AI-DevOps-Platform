import logging
import time

from sqlalchemy import inspect, text
from sqlalchemy.exc import OperationalError

from app.database.base import Base
from app.database.connection import engine

# Import every model here so Base knows about it
from app.models.user import User  # noqa: F401
from app.models.chat import Chat  # noqa: F401

log = logging.getLogger(__name__)


def wait_for_db(retries: int = 30, delay: float = 2.0):
    """
    Postgres may still be booting when the backend starts
    (depends_on does not wait for it), so retry for a while.
    """
    for attempt in range(1, retries + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return
        except OperationalError:
            log.warning("Database not ready (attempt %s/%s), retrying...", attempt, retries)
            time.sleep(delay)

    raise RuntimeError("Database is not reachable")


def create_tables():
    """
    Create all database tables.
    This runs automatically when FastAPI starts.
    """
    wait_for_db()
    Base.metadata.create_all(bind=engine)

    # chat_history existed before users were added: add the column if missing
    columns = [c["name"] for c in inspect(engine).get_columns("chat_history")]
    if "user_id" not in columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE chat_history ADD COLUMN user_id INTEGER REFERENCES users(id)"))
