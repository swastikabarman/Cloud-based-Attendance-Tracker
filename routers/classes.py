from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
from sqlalchemy import text

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def create_class(class_name: str, teacher_id: int, db: Session = Depends(get_db)):
    db.execute(
        text("INSERT INTO classes (class_name, teacher_id) VALUES (:name, :tid)"),
        {"name": class_name, "tid": teacher_id}
    )
    db.commit()
    return {"message": "Class created successfully"}

