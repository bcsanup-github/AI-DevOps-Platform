import re

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.templating import templates
from app.services.auth_service import AuthService

router = APIRouter()

USERNAME_RE = re.compile(r"^[A-Za-z0-9_.-]{3,50}$")


class Credentials(BaseModel):
    username: str
    password: str


def current_user(request: Request, db: Session = Depends(get_db)) -> User | None:
    user_id = request.session.get("user_id")
    if user_id is None:
        return None
    return db.get(User, user_id)


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, user: User | None = Depends(current_user)):

    if user:
        return RedirectResponse("/", status_code=303)

    return templates.TemplateResponse(request, "login.html")


@router.post("/api/register")
def register(creds: Credentials, request: Request, db: Session = Depends(get_db)):

    username = creds.username.strip()

    if not USERNAME_RE.match(username):
        return JSONResponse(
            {"detail": "Username must be 3-50 characters: letters, numbers, . _ -"},
            status_code=400
        )

    if len(creds.password) < 8:
        return JSONResponse({"detail": "Password must be at least 8 characters."}, status_code=400)

    if db.query(User).filter(User.username == username).first():
        return JSONResponse({"detail": "That username is already taken."}, status_code=409)

    user = User(username=username, password_hash=AuthService.hash_password(creds.password))
    db.add(user)
    db.commit()
    db.refresh(user)

    request.session["user_id"] = user.id

    return {"username": user.username}


@router.post("/api/login")
def login(creds: Credentials, request: Request, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.username == creds.username.strip()).first()

    if not user or not AuthService.verify_password(creds.password, user.password_hash):
        return JSONResponse({"detail": "Wrong username or password."}, status_code=401)

    request.session["user_id"] = user.id

    return {"username": user.username}


@router.post("/logout")
def logout(request: Request):

    request.session.clear()

    return RedirectResponse("/login", status_code=303)
