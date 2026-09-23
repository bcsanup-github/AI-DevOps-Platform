from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.auth import current_user
from app.config import OLLAMA_MODEL
from app.database.connection import get_db
from app.models.chat import Chat
from app.models.user import User
from app.templating import templates
from app.services.ai_service import AIService

router = APIRouter()


class ChatRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=8000)


@router.get("/", response_class=HTMLResponse)
def index(request: Request, user: User | None = Depends(current_user)):

    if not user:
        return RedirectResponse("/login", status_code=303)

    return templates.TemplateResponse(
        request,
        "index.html",
        {"username": user.username, "model": OLLAMA_MODEL}
    )


@router.get("/api/history")
def history(user: User | None = Depends(current_user), db: Session = Depends(get_db)):

    if not user:
        return JSONResponse({"detail": "Not logged in."}, status_code=401)

    chats = (
        db.query(Chat)
        .filter(Chat.user_id == user.id)
        .order_by(Chat.id.desc())
        .limit(50)
        .all()
    )

    return [
        {"id": c.id, "question": c.question, "answer": c.answer}
        for c in reversed(chats)
    ]


# Plain "def" (not async) so the slow Ollama call runs in a
# worker thread instead of freezing the whole server.
@router.post("/chat")
def chat(data: ChatRequest, user: User | None = Depends(current_user), db: Session = Depends(get_db)):

    if not user:
        return JSONResponse({"detail": "Not logged in."}, status_code=401)

    prompt = data.prompt.strip()

    answer = AIService.generate(prompt)

    db.add(Chat(user_id=user.id, question=prompt, answer=answer))
    db.commit()

    return {
        "response": answer
    }


@router.delete("/api/history")
def clear_history(user: User | None = Depends(current_user), db: Session = Depends(get_db)):

    if not user:
        return JSONResponse({"detail": "Not logged in."}, status_code=401)

    db.query(Chat).filter(Chat.user_id == user.id).delete()
    db.commit()

    return {"status": "cleared"}
