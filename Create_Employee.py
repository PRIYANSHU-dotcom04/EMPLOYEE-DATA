from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field,ValidationError
from typing import Annotated, Literal, Optional
import json

app = FastAPI()

# ------------------- MODEL DATA ------------------------
class Employee(BaseModel):
    emp_id: Annotated[str, Field(...)]
    name: Annotated[str, Field(..., max_length=60)]
    city: Annotated[str, Field(..., max_length=50)]
    age: Annotated[int, Field(..., gt=0, lt=120)]
    gender: Annotated[Literal['male', 'female', 'others'], Field(...)]
    department: Annotated[Literal[
        'Manager', 'HR', 'Finance', 'Marketing', 'Sales', 'IT', 'Operations',
        'Customer Support', 'Legal', 'Administration', 'Research & Development',
        'Production', 'Quality Assurance', 'Logistics', 'Procurement', 'Training',
        'Public Relations', 'Business Development'
    ], Field(...)]
    Experience: Annotated[int, Field(..., le=60, ge=1)]

 
#--------------------------- UPDATE MODEL --------------------------- 
class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    city: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[Literal['male', 'female', 'others']] = None
    department: Optional[Literal[
        'Manager', 'HR', 'Finance', 'Marketing', 'Sales', 'IT', 'Operations',
        'Customer Support', 'Legal', 'Administration', 'Research & Development',
        'Production', 'Quality Assurance', 'Logistics', 'Procurement', 'Training',
        'Public Relations', 'Business Development'
    ]] = None
    Experience: Optional[int] = None


# ---------------- PAST DATA ----------------
def past_data():
    try:
        with open('Employee.json', 'r') as r:
            return json.load(r)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}  


# ---------------- NEW DATA ----------------
def new_data(data):
    with open('Employee.json', 'w') as w:
        json.dump(data, w, indent=4)


# ---------------- HOME ----------------
@app.get('/home')
def home():
    return {"message": "API is working !!!!"}


# ---------------- SHOW ----------------
@app.get("/show/{emp_id}")
def show_data(emp_id: str):
    data = past_data()

    if emp_id not in data:
        raise HTTPException(status_code=404, detail="Employee not found !!!")

    return data[emp_id]


# ---------------- CREATE ----------------
@app.post('/create')
def create_employe(employee: Employee):

    data = past_data()

    if employee.emp_id in data:
        raise HTTPException(status_code=400, detail='Employee already exists')

    data[employee.emp_id] = employee.model_dump(exclude=['emp_id'])

    new_data(data)

    return JSONResponse(status_code=201, content={'message': 'Employee created successfully'})


# ---------------- UPDATE ----------------

@app.put("/update/{emp_id}")
def update_employee(emp_id: str, emp_update: EmployeeUpdate):

    data = past_data()

    if emp_id not in data:
        raise HTTPException(status_code=400, detail='Employee not exist')

    existing_data = data[emp_id]

    update_data = emp_update.model_dump(exclude_unset=True)

    clean_data = {}

    for key, value in update_data.items():
        if value not in ["string", 0, None]:
            clean_data[key] = value

    if not clean_data:
        raise HTTPException(status_code=400, detail='No valid data provided')

    existing_data.update(clean_data)

    existing_data["emp_id"] = emp_id
    validated = Employee(**existing_data)

    data[emp_id] = validated.model_dump(exclude=['emp_id'])

    new_data(data)

    return JSONResponse(
        status_code=200,
        content={
            'message': 'Employee updated successfully',
            'updated_data': data[emp_id]
        }
    )

# ---------------- SALARY ----------------
department_base_salary = {
    "Manager": 30000,
    "HR": 15000,
    "Finance": 22000,
    "Marketing": 20000,
    "Sales": 18000,
    "IT": 20000,
    "Operations": 21000,
    "Customer Support": 14000,
    "Legal": 25000,
    "Administration": 16000,
    "Research & Development": 26000,
    "Production": 19000,
    "Quality Assurance": 17000,
    "Logistics": 18000,
    "Procurement": 17500,
    "Training": 16000,
    "Public Relations": 19000,
    "Business Development": 23000
}


def calculate_salary(emp):
    dept = emp["department"]
    experience = emp["Experience"]

    if dept not in department_base_salary:
        raise HTTPException(status_code=400, detail="Invalid Department")

    base_salary = department_base_salary[dept]

    experience_bonus = base_salary * (0.05 * experience)
    hra = base_salary * 0.20
    da = base_salary * 0.10
    bonus = 2000 if experience > 2 else 1000
    pf = base_salary * 0.12

    total_salary = base_salary + experience_bonus + hra + da + bonus
    net_salary = total_salary - pf

    return {
        "id": emp["emp_id"],
        "name": emp["name"],
        "department": dept,
        "experience": experience,
        "base_salary": base_salary,
        "experience_bonus": experience_bonus,
        "hra": hra,
        "da": da,
        "bonus": bonus,
        "pf": pf,
        "net_salary": net_salary,
        "total_salary": total_salary
    }


@app.get("/salary/{emp_id}")
def get_salary(emp_id: str):

    data = past_data()

    if emp_id not in data:
        raise HTTPException(status_code=404, detail="Employee not found")

    emp = data[emp_id]
    emp["emp_id"] = emp_id

    return calculate_salary(emp)




