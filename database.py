import os

import mysql.connector
from dotenv import load_dotenv
from mysql.connector import MySQLConnection


load_dotenv()


def get_connection() -> MySQLConnection:
    """Open and return a connection to the employee_management database."""
    required_settings = ("DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME")
    missing_settings = [
        setting for setting in required_settings if not os.getenv(setting)
    ]

    if missing_settings:
        missing_names = ", ".join(missing_settings)
        raise ValueError(
            f"Missing database settings: {missing_names}. "
            "Add them to the local .env file."
        )

    return mysql.connector.connect(
        host=os.environ["DB_HOST"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
    )
