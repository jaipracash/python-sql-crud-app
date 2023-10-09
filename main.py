from datetime import datetime, date
import MySQLdb
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, EmailStr
import uvicorn

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'jai',
    'passwd': 'admin123',
    'db': 'student_tracker',
}

# Create a connection to the database
conn = MySQLdb.connect(**db_config)

app = FastAPI(title='Student tracker', description='API for managing student records', version='1.0.0')


# Pydantic model to define the schema of the data
class Student(BaseModel):
    name: str
    dob: date
    reg_number: int
    email: str
    address: str = None

@app.post("/students_registration", response_model=Student)
def create(student: Student):
    cursor = conn.cursor()
    query = "INSERT INTO students(name, dob, reg_number, email, address) VALUES(%s, %s, %s, %s, %s)"
    cursor.execute(query, (student.name, student.dob, student.reg_number, student.email, student.address))
    conn.commit()
    # student.id = cursor.lastrowid
    cursor.close()
    return student

@app.get("/students/{reg_number}", response_model= Student)
def read_one(reg_number: int):
    cursor = conn.cursor()
    query = "SELECT name, dob, reg_number, email, address FROM students WHERE reg_number = %s"
    cursor.execute(query, (reg_number,))
    student = cursor.fetchone()
    cursor.close()
    if  student[4] == None:
        return {"name": student[0], "dob": student[1], "reg_number": student[2], "email": student[3] }

    return {"name": student[0], "dob": student[1], "reg_number": student[2], "email": student[3], "address": student[4]}

@app.get("/students", response_model= list[Student])
def read_all():
    cursor = conn.cursor()
    query = "select * from students"
    cursor.execute(query)
    students = cursor.fetchall()
    students_data = []
    for student in students:
        address = ""
        if student[4] != None:
            address = student[4]

        student_dict = {
            "name": student[0],
            "dob": student[1],
            "reg_number": student[2],
            "email": student[3],
            "address": address
        }
        students_data.append(student_dict)
    cursor.close()
    return students_data

@app.put("/students/{reg_number}", response_model= Student)
def update_student(reg_number: int, student: Student):
    cursor = conn.cursor()
    query = "update students set name = %s, dob = %s, email = %s, address = %s where reg_number = %s"
    cursor.execute(query, (student.name, student.dob, student.email, student.address, student.reg_number))
    conn.commit()
    cursor.close()
    student.reg_number = reg_number
    return student

@app.delete("/students/{reg_number}")
def delete_item(reg_number: int):
    cursor = conn.cursor()
    query = "delete from students where reg_number = %s"
    cursor.execute(query, (reg_number,))
    conn.commit()
    cursor.close()
    return {"reg_number": reg_number}





if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8081)
