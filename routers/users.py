from passlib.context import CryptContext
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
from auth import create_access_token
from sqlalchemy import select
router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)


@router.post("/")
def create_user(name: str, email: str, password: str, role: str, db: Session = Depends(get_db)):
    hashed_password = hash_password(password)

    new_user = User(
        name=name,
        email=email,
        password=hashed_password,
        role=role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user



@router.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.execute(
        select(User).where(User.email == email)
    ).scalar_one_or_none()

    if not user:
        return {"error": "User not found"}

    if not pwd_context.verify(password, user.password):
        return {"error": "Invalid password"}

    token = create_access_token({
    "sub": user.email,
    "role": user.role
    })

    return {"access_token": token}
