from fastapi import FastAPI
import mysql.connector
from pydantic import BaseModel

app = FastAPI(title="Employee Management")

# Pydantic model - idhu swalpa tappadre 422 baruthe
class Employee(BaseModel):
    name: str
    email: str
    department: str
    salary: int

# DB connection
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="employee_db"
    )

@app.get("/")
def home():
    return {"message": "API Working"}

@app.post("/employees")
def create_employee(emp: Employee):
    db = get_db()
    cursor = db.cursor()
    query = "INSERT INTO employees (name, email, department, salary) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (emp.name, emp.email, emp.department, emp.salary))
    db.commit()
    db.close()
    return {"message": "Employee added", "data": emp}

@app.get("/employees")
def get_employees():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM employees")
    result = cursor.fetchall()
    db.close()
    return result