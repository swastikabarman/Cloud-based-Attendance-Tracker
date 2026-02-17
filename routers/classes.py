from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
from sqlalchemy import text
from fastapi import HTTPException

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")

def create_class(class_name: str, teacher_id: int, db: Session = Depends(get_db)):

    teacher = db.execute(
        text("SELECT * FROM users WHERE id = :tid"),
        {"tid": teacher_id}
    ).fetchone()

    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    result = db.execute(
        text("""
            INSERT INTO classes (class_name, teacher_id)
            VALUES (:name, :tid)
            RETURNING id
        """),
        {"name": class_name, "tid": teacher_id}
    )
    class_id = result.fetchone()[0] 
    db.commit()
    return {
        "message": "Class created successfully",
        "class_id": class_id
    }



