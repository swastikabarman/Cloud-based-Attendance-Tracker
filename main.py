from database import engine, Base
import models
from fastapi import FastAPI
from routers import users, classes, attendance

app = FastAPI()
Base.metadata.create_all(bind=engine)

app.include_router(users.router, prefix="/users")
app.include_router(classes.router, prefix="/classes")
app.include_router(attendance.router, prefix="/attendance")

@app.get("/")
def home():
    return {"message": "Attendance System Running"}


