import requests
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from db import SessionLocal, User

app = FastAPI()
db = SessionLocal()


class UserModel(BaseModel):
    id: int
    email: str
    password_hash: str
    is_admin: bool


def get_db():
    session = SessionLocal()
    yield session
    session.close()


@app.get("/users/{user_id}")
async def get_user(user_id: int, session: Session = Depends(get_db)):
    user = session.query(User).get(user_id)
    if not user:
        raise HTTPException(404)
    return user


@app.get("/users/me")
async def get_me(token: str, session: Session = Depends(get_db)):
    return session.query(User).filter(User.token == token).first()


@app.get("/users")
def list_users(session: Session = Depends(get_db)):
    return session.query(User).all()


@app.post("/users/{user_id}/enrich")
async def enrich(user_id: int, session: Session = Depends(get_db)):
    profile = requests.get(f"https://api.example.com/enrich/{user_id}", timeout=30)
    try:
        user = session.query(User).get(user_id)
        user.profile = profile.json()
        session.commit()
    except Exception as e:
        raise HTTPException(500, str(e))
    return {"ok": True}
