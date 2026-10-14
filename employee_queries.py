from typing import Any

from mysql.connector import MySQLConnection

from database import get_connection


Employee = dict[str, Any]


def add_employee(employee: Employee) -> Employee:
    connection: MySQLConnection = get_connection()
    cursor = None

    try:
        cursor = connection.cursor()
        query = """
            INSERT INTO employees (name, email, department, salary)
            VALUES (%s, %s, %s, %s)
        """
        values = (
            employee["name"],
            employee["email"],
            employee["department"],
            employee["salary"],
        )
        cursor.execute(query, values)
        connection.commit()
        return {"id": cursor.lastrowid, **employee}
    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


def get_all_employees() -> list[Employee]:
    connection: MySQLConnection = get_connection()
    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, name, email, department, salary "
            "FROM employees ORDER BY id"
        )
        return cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


def get_employee_by_id(employee_id: int) -> Employee | None:
    connection: MySQLConnection = get_connection()
    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, name, email, department, salary "
            "FROM employees WHERE id = %s",
            (employee_id,),
        )
        return cursor.fetchone()
    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


def update_employee(employee_id: int, employee: Employee) -> Employee | None:
    connection: MySQLConnection = get_connection()
    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT id FROM employees WHERE id = %s FOR UPDATE",
            (employee_id,),
        )
        if cursor.fetchone() is None:
            return None

        query = """
            UPDATE employees
            SET name = %s, email = %s, department = %s, salary = %s
            WHERE id = %s
        """
        values = (
            employee["name"],
            employee["email"],
            employee["department"],
            employee["salary"],
            employee_id,
        )
        cursor.execute(query, values)
        connection.commit()
        return {"id": employee_id, **employee}
    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


def delete_employee(employee_id: int) -> bool:
    connection: MySQLConnection = get_connection()
    cursor = None

    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM employees WHERE id = %s", (employee_id,))
        connection.commit()
        return cursor.rowcount > 0
    finally:
        if cursor is not None:
            cursor.close()
        connection.close()
