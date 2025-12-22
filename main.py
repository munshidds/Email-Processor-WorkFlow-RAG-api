from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


class StudentBase(BaseModel):
    name: str
    age: int
    grade: str


class Student(StudentBase):
    id: int


app = FastAPI(title="Simple Student Management System")

# Allow local JS/HTML to call the API easily
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory "database"
students: List[Student] = []
next_id: int = 1

# Serve static frontend files (HTML/JS/CSS)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/api/students", response_model=List[Student])
def list_students() -> List[Student]:
    return students


@app.post("/api/students", response_model=Student, status_code=201)
def create_student(student: StudentBase) -> Student:
    global next_id
    new_student = Student(id=next_id, **student.model_dict())
    next_id += 1
    students.append(new_student)
    return new_student


@app.put("/api/students/{student_id}", response_model=Student)
def update_student(student_id: int, updated: StudentBase) -> Student:
    for index, s in enumerate(students):
        if s.id == student_id:
            students[index] = Student(id=student_id, **updated.model_dict())
            return students[index]
    raise HTTPException(status_code=404, detail="Student not found")


@app.delete("/api/students/{student_id}", status_code=204)
def delete_student(student_id: int) -> None:
    for index, s in enumerate(students):
        if s.id == student_id:
            students.pop(index)
            return None
    raise HTTPException(status_code=404, detail="Student not found")


@app.get("/", include_in_schema=False)
def root() -> FileResponse:
    # Serve the main UI
    return FileResponse("static/index.html")


