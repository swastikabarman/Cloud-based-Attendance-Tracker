from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date
import matplotlib.pyplot as plt

from database import SessionLocal
from auth import verify_token

router = APIRouter(prefix="/attendance", tags=["Attendance"])


# Database Dependency

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Teacher: Mark Attendance (Role Protected)

@router.post("/")
def mark_attendance(
    student_id: int,
    class_id: int,
    status: str,
    token: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if token.get("role") != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can mark attendance")

    db.execute(
        text("""
        INSERT INTO attendance (student_id, class_id, attendance_date, status)
        VALUES (:sid, :cid, :adate, :status)
        """),
        {
            "sid": student_id,
            "cid": class_id,
            "adate": date.today(),
            "status": status
        }
    )
    db.commit()

    return {"message": "Attendance marked successfully"}


# Overall Attendance Percentage

@router.get("/percentage/{student_id}")
def attendance_percentage(
    student_id: int,
    token: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    result = db.execute(
        text("""
        SELECT COUNT(*) as total,
               SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as present
        FROM attendance
        WHERE student_id = :sid
        """),
        {"sid": student_id}
    ).fetchone()

    total = result.total or 0
    present = result.present or 0

    if total == 0:
        return {"percentage": 0}

    percentage = (present / total) * 100
    return {"percentage": round(percentage, 2)}


# Subject-wise Attendance

@router.get("/subject/{student_id}")
def subject_wise_attendance(
    student_id: int,
    token: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    result = db.execute(
        text("""
        SELECT c.class_name,
               COUNT(*) as total,
               SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) as present
        FROM attendance a
        JOIN classes c ON a.class_id = c.id
        WHERE a.student_id = :sid
        GROUP BY c.class_name
        """),
        {"sid": student_id}
    ).fetchall()

    data = []

    for row in result:
        total = row.total or 0
        present = row.present or 0

        percentage = 0
        if total > 0:
            percentage = (present / total) * 100

        data.append({
            "subject": row.class_name,
            "attendance_percentage": round(percentage, 2)
        })

    return data


# Graph Data (JSON)

@router.get("/graph/{student_id}")
def attendance_graph_data(
    student_id: int,
    token: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    return subject_wise_attendance(student_id, token, db)


# Graph Image (PNG)

@router.get("/graph-image/{student_id}")
def attendance_graph_image(
    student_id: int,
    token: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    result = subject_wise_attendance(student_id, token, db)

    if not result:
        raise HTTPException(status_code=404, detail="No attendance data found")

    subjects = [item["subject"] for item in result]
    percentages = [item["attendance_percentage"] for item in result]

    plt.figure()
    plt.bar(subjects, percentages)
    plt.xlabel("Subjects")
    plt.ylabel("Attendance %")
    plt.title("Subject-wise Attendance")
    plt.xticks(rotation=45)
    plt.tight_layout()

    file_path = f"attendance_graph_{student_id}.png"
    plt.savefig(file_path)
    plt.close()

    return FileResponse(file_path, media_type="image/png")


# Monthly Attendance Percentage (PostgreSQL Syntax)

@router.get("/monthly-percentage/{student_id}")
def monthly_attendance_percentage(
    student_id: int,
    month: int,
    year: int,
    token: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    result = db.execute(
        text("""
        SELECT COUNT(*) as total,
               SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as present
        FROM attendance
        WHERE student_id = :sid
        AND EXTRACT(MONTH FROM attendance_date) = :month
        AND EXTRACT(YEAR FROM attendance_date) = :year
        """),
        {"sid": student_id, "month": month, "year": year}
    ).fetchone()

    total = result.total or 0
    present = result.present or 0

    if total == 0:
        return {"percentage": 0}

    percentage = (present / total) * 100
    return {"percentage": round(percentage, 2)}


# Monthly Subject-wise Graph Image (PostgreSQL)

@router.get("/monthly-graph-image/{student_id}")
def monthly_graph_image(
    student_id: int,
    month: int,
    year: int,
    token: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    result = db.execute(
        text("""
        SELECT c.class_name,
               COUNT(*) as total,
               SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) as present
        FROM attendance a
        JOIN classes c ON a.class_id = c.id
        WHERE a.student_id = :sid
        AND EXTRACT(MONTH FROM a.attendance_date) = :month
        AND EXTRACT(YEAR FROM a.attendance_date) = :year
        GROUP BY c.class_name
        """),
        {"sid": student_id, "month": month, "year": year}
    ).fetchall()

    subjects = []
    percentages = []

    for row in result:
        total = row.total or 0
        present = row.present or 0

        percentage = 0
        if total > 0:
            percentage = (present / total) * 100

        subjects.append(row.class_name)
        percentages.append(round(percentage, 2))

    if not subjects:
        raise HTTPException(status_code=404, detail="No monthly data found")

    plt.figure()
    plt.bar(subjects, percentages)
    plt.xlabel("Subjects")
    plt.ylabel("Attendance %")
    plt.title(f"Attendance for {month}/{year}")
    plt.xticks(rotation=45)
    plt.tight_layout()

    file_path = f"monthly_attendance_{student_id}_{month}_{year}.png"
    plt.savefig(file_path)
    plt.close()

    return FileResponse(file_path, media_type="image/png")



