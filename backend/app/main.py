from fastapi import FastAPI, Request, Body
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database.init_db import create_tables
from app.database.connection import SessionLocal
from app.models.chat import Chat
from app.services.ai_service import AIService

app = FastAPI(title="AI DevOps Project")

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static"
)

templates = Jinja2Templates(directory="app/templates")


@app.on_event("startup")
def startup():

    create_tables()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request
        }
    )


@app.post("/chat")
async def chat(data: dict = Body(...)):

    prompt = data["prompt"]

    answer = AIService.generate(prompt)

    db = SessionLocal()

    chat = Chat(
        question=prompt,
        answer=answer
    )

    db.add(chat)
    db.commit()
    db.refresh(chat)
    db.close()

    return {
        "response": answer
    }


@app.get("/health")
async def health():

    return {
        "status": "healthy"
    }