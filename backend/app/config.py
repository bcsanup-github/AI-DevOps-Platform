import os

from dotenv import load_dotenv

load_dotenv()


def _database_url() -> str:
    # DATABASE_URL wins if set (handy for local testing with sqlite)
    if os.getenv("DATABASE_URL"):
        return os.environ["DATABASE_URL"]

    return (
        f"postgresql://"
        f"{os.getenv('POSTGRES_USER', 'postgres')}:"
        f"{os.getenv('POSTGRES_PASSWORD', 'postgres')}@"
        f"{os.getenv('POSTGRES_HOST', 'localhost')}:"
        f"{os.getenv('POSTGRES_PORT', '5432')}/"
        f"{os.getenv('POSTGRES_DB', 'chat_history')}"
    )


DATABASE_URL = _database_url()

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")

# Used to sign the login session cookie. MUST be set in production.
SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
