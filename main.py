import logging
import math
from typing import Any

import mysql.connector
from fastapi import FastAPI, HTTPException, Path
from fastapi.responses import JSONResponse
from starlette.requests import Request

import employee_queries
import file_operations


logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

app = FastAPI(title="Employee Management API")

EMPLOYEE_FIELDS = {"name", "email", "department", "salary"}


def get_required_text(data: dict[str, Any], field: str) -> str:
    if set(data) != {field}:
        raise HTTPException(
            status_code=422,
            detail=f"Request body must contain only the {field} field.",
        )
    value = data[field]
    if not isinstance(value, str):
        raise HTTPException(
            status_code=422,
            detail=f"{field} must be a string.",
        )
    return value


def validate_employee(data: dict[str, Any]) -> dict[str, Any]:
    """Check and normalize the four required employee fields."""
    missing_fields = EMPLOYEE_FIELDS - data.keys()
    if missing_fields:
        raise HTTPException(
            status_code=422,
            detail=f"Missing required fields: {', '.join(sorted(missing_fields))}",
        )

    extra_fields = data.keys() - EMPLOYEE_FIELDS
    if extra_fields:
        raise HTTPException(
            status_code=422,
            detail=f"Unexpected fields: {', '.join(sorted(extra_fields))}",
        )

    employee: dict[str, Any] = {}
    maximum_lengths = {"name": 100, "email": 255, "department": 100}
    for field, maximum_length in maximum_lengths.items():
        value = data[field]
        if not isinstance(value, str) or not value.strip():
            raise HTTPException(
                status_code=422,
                detail=f"{field} must be a non-empty string.",
            )
        value = value.strip()
        if len(value) > maximum_length:
            raise HTTPException(
                status_code=422,
                detail=f"{field} must be at most {maximum_length} characters.",
            )
        employee[field] = value

    if "@" not in employee["email"]:
        raise HTTPException(
            status_code=422,
            detail="email must contain an @ symbol.",
        )

    salary = data["salary"]
    if (
        isinstance(salary, bool)
        or not isinstance(salary, (int, float))
        or not math.isfinite(salary)
        or salary < 0
        or salary > 99_999_999.99
    ):
        raise HTTPException(
            status_code=422,
            detail="salary must be between 0 and 99999999.99.",
        )
    employee["salary"] = salary
    return employee


@app.exception_handler(mysql.connector.Error)
async def handle_database_error(
    request: Request, error: mysql.connector.Error
) -> JSONResponse:
    if isinstance(error, mysql.connector.IntegrityError) and error.errno == 1062:
        return JSONResponse(
            status_code=409,
            content={"detail": "An employee with that email already exists."},
        )

    logger.error(
        "MySQL operation failed while handling %s: %s",
        request.url.path,
        error,
        exc_info=(type(error), error, error.__traceback__),
    )
    return JSONResponse(
        status_code=503,
        content={"detail": "Database operation failed. Check the MySQL server and settings."},
    )


@app.exception_handler(ValueError)
async def handle_configuration_error(
    request: Request, error: ValueError
) -> JSONResponse:
    logger.error("Database configuration error while handling %s: %s", request.url.path, error)
    return JSONResponse(status_code=503, content={"detail": str(error)})


@app.exception_handler(file_operations.InvalidFileNameError)
async def handle_invalid_file_name(
    request: Request, error: file_operations.InvalidFileNameError
) -> JSONResponse:
    logger.info("Rejected file request at %s: %s", request.url.path, error)
    return JSONResponse(status_code=422, content={"detail": str(error)})


@app.exception_handler(FileNotFoundError)
async def handle_missing_file(request: Request, error: FileNotFoundError) -> JSONResponse:
    logger.info("Missing file requested at %s: %s", request.url.path, error)
    return JSONResponse(status_code=404, content={"detail": "Text file not found."})


@app.exception_handler(FileExistsError)
async def handle_existing_file(request: Request, error: FileExistsError) -> JSONResponse:
    logger.info("Existing file conflict at %s: %s", request.url.path, error)
    return JSONResponse(status_code=409, content={"detail": "Text file already exists."})


@app.exception_handler(PermissionError)
async def handle_file_permission_error(
    request: Request, error: PermissionError
) -> JSONResponse:
    logger.error("File permission error while handling %s: %s", request.url.path, error)
    return JSONResponse(status_code=403, content={"detail": "Permission denied for this file."})


@app.exception_handler(OSError)
async def handle_file_system_error(request: Request, error: OSError) -> JSONResponse:
    logger.error(
        "File operation failed while handling %s: %s",
        request.url.path,
        error,
        exc_info=(type(error), error, error.__traceback__),
    )
    return JSONResponse(status_code=500, content={"detail": "File operation failed."})


@app.post("/employees", status_code=201)
def create_employee(data: dict[str, Any]) -> dict[str, Any]:
    employee = validate_employee(data)
    return employee_queries.add_employee(employee)


@app.get("/employees")
def read_employees() -> list[dict[str, Any]]:
    return employee_queries.get_all_employees()


@app.get("/employees/{employee_id}")
def read_employee(
    employee_id: int = Path(gt=0),
) -> dict[str, Any]:
    employee = employee_queries.get_employee_by_id(employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found.")
    return employee


@app.put("/employees/{employee_id}")
def replace_employee(
    data: dict[str, Any],
    employee_id: int = Path(gt=0),
) -> dict[str, Any]:
    employee = validate_employee(data)
    updated_employee = employee_queries.update_employee(employee_id, employee)
    if updated_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found.")
    return updated_employee


@app.delete("/employees/{employee_id}")
def remove_employee(
    employee_id: int = Path(gt=0),
) -> dict[str, str]:
    deleted = employee_queries.delete_employee(employee_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Employee not found.")
    return {"message": "Employee deleted successfully."}


@app.post("/files/text/{filename}", status_code=201)
def create_text_file(filename: str) -> dict[str, str]:
    created_filename = file_operations.create_text_file(filename)
    return {"message": "Text file created.", "filename": created_filename}


@app.put("/files/text/{filename}")
def write_text_file(filename: str, data: dict[str, Any]) -> dict[str, Any]:
    content = get_required_text(data, "content")
    characters_written = file_operations.write_text_file(filename, content)
    return {"message": "Text file written.", "characters_written": characters_written}


@app.post("/files/text/{filename}/append")
def append_text_file(filename: str, data: dict[str, Any]) -> dict[str, Any]:
    content = get_required_text(data, "content")
    characters_written = file_operations.append_text_file(filename, content)
    return {"message": "Content appended.", "characters_written": characters_written}


@app.get("/files/text/{filename}")
def read_text_file(filename: str) -> dict[str, str]:
    return {"filename": filename, "content": file_operations.read_text_file(filename)}


@app.get("/files/text/{filename}/lines")
def read_text_file_lines(filename: str) -> dict[str, Any]:
    return {"filename": filename, "lines": file_operations.read_text_file_lines(filename)}


@app.get("/files/text/{filename}/exists")
def check_text_file_exists(filename: str) -> dict[str, Any]:
    return {"filename": filename, "exists": file_operations.text_file_exists(filename)}


@app.post("/files/text/{filename}/rename")
def rename_text_file(filename: str, data: dict[str, Any]) -> dict[str, str]:
    new_filename = get_required_text(data, "new_filename")
    renamed_filename = file_operations.rename_text_file(filename, new_filename)
    return {"message": "Text file renamed.", "filename": renamed_filename}


@app.post("/files/text/{filename}/copy", status_code=201)
def copy_text_file(filename: str, data: dict[str, Any]) -> dict[str, str]:
    copy_filename = get_required_text(data, "copy_filename")
    copied_filename = file_operations.copy_text_file(filename, copy_filename)
    return {"message": "Text file copied.", "filename": copied_filename}


@app.delete("/files/text/{filename}")
def delete_text_file(filename: str) -> dict[str, str]:
    file_operations.delete_text_file(filename)
    return {"message": "Text file deleted."}


@app.get("/files/text/{filename}/size")
def get_text_file_size(filename: str) -> dict[str, Any]:
    size_bytes = file_operations.get_text_file_size(filename)
    return {"filename": filename, "size_bytes": size_bytes}
