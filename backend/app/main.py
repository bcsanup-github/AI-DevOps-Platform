from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.api import auth, chat, health
from app.config import SECRET_KEY
from app.database.init_db import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):

    create_tables()

    yield


app = FastAPI(title="AI DevOps Project", lifespan=lifespan)

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    session_cookie="ai_session",
    max_age=60 * 60 * 24 * 7,
    same_site="lax"
)

@app.middleware("http")
async def revalidate_static(request: Request, call_next):

    response = await call_next(request)

    # Browsers must check with the server before reusing old CSS/JS
    if request.url.path.startswith("/static/"):
        response.headers["Cache-Control"] = "no-cache"

    return response


app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static"
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(chat.router)
