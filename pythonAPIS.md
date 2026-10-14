# Python API Project Guide

This guide describes the project files as they are currently written. In particular, it reflects the current `main.py`, not routes from an earlier version of the project.

## What is `requirements.txt`?

`requirements.txt` is a plain-text list of Python packages the project expects to install. It lets another developer install those dependencies in one command:

```powershell
python -m pip install -r requirements.txt
```

The current file lists:

| Requirement | What it is for |
| --- | --- |
| `fastapi` | Defining HTTP API routes and handling requests |
| `uvicorn` | Running the FastAPI application as a web server |
| `mysql-connector-python` | Connecting Python code to MySQL |
| `python-multipart` | Parsing multipart form data, commonly needed for file uploads |
| `python-dotenv` | Loading local configuration from a `.env` file |

The list usually contains direct, third-party dependencies that the application needs. It does not usually list Python's built-in modules, such as `os`, `pathlib`, or `shutil`. Dependencies of the listed packages may be installed automatically. To make installations reproducible, a project can pin versions, for example `fastapi==<tested-version>`, or use a lock file. This project's current requirements do not pin versions.

## What is a Python virtual environment?

A virtual environment is an isolated Python installation for one project. It keeps that project's installed packages separate from other projects and from the system Python.

This project uses `.venv`. In PowerShell, create and activate it from the project folder:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

After activation, the terminal prompt typically starts with `(.venv)`. The `.venv` directory should not be committed to Git; this project's `.gitignore` excludes it.

## What is FastAPI?

FastAPI is a Python framework for building HTTP APIs. A route decorator such as `@app.get("/employees")` connects an HTTP method and URL path to a Python function. FastAPI uses type annotations and Pydantic models to validate request data and generate interactive API documentation, usually at `/docs`.

In this project, `app = FastAPI(...)` creates the application. Uvicorn serves it with:

```powershell
python -m uvicorn main:app --reload
```

Here, `main` means `main.py`, `app` is the FastAPI application variable, and `--reload` restarts the development server when code changes.

## How do Python APIs differ from Node.js projects?

Both can build HTTP APIs and use routes, JSON, database drivers, and HTTP status codes. The differences below are common conventions, not strict limitations:

| Topic | Python example in this project | Common Node.js equivalent |
| --- | --- | --- |
| Runtime | Python interpreter | Node.js runtime |
| Package manifest | `requirements.txt` | `package.json` (often with a lock file) |
| Install dependencies | `python -m pip install -r requirements.txt` | `npm install` |
| Web framework | FastAPI | Express, Fastify, or NestJS |
| Run the server | Uvicorn runs `main:app` | `node server.js` or an npm script |
| Async style | Supports `async def`; sync functions are also common | JavaScript commonly uses promises and `async`/`await` for I/O |
| Request validation | Type annotations and Pydantic models | Middleware, schemas, or TypeScript types plus runtime validation |
| Virtual environments | Commonly one `.venv` per project | Dependencies are normally installed per project under `node_modules` |

Neither language is inherently the right choice for every API. Choose based on project needs, team experience, libraries, and deployment environment.

## Routes currently registered in `main.py`

The current `main.py` registers these three routes. Run the app and visit `http://127.0.0.1:8000/docs` to inspect or try them.

| Method | Path | Current behavior | Typical success |
| --- | --- | --- | --- |
| `GET` | `/` | Returns `{"message": "API Working"}` | `200 OK` |
| `POST` | `/employees` | Validates an employee with the `Employee` Pydantic model, inserts it into MySQL, commits, then returns a message and the employee data | `200 OK` by default |
| `GET` | `/employees` | Selects all employees and returns the rows as JSON dictionaries | `200 OK` |

The POST request body must have all four model fields: `name` (string), `email` (string), `department` (string), and `salary` (integer). For example:

```json
{
  "name": "Sakshi",
  "email": "sakshi@example.com",
  "department": "Computer Applications",
  "salary": 50000
}
```

Do not include `id` in this POST body: the current model does not define it, and MySQL is expected to generate it. FastAPI/Pydantic normally returns `422 Unprocessable Entity` when required model fields are missing or have incompatible types.

### Implemented helpers that are not currently API routes

`employee_queries.py` defines Python functions for adding, listing, finding, updating, and deleting employees. `file_operations.py` defines text-file helper functions. However, the current `main.py` does not import those modules or register routes for them. A Python function in a project is not automatically an HTTP API endpoint; it must be connected to the FastAPI app with a route decorator.

So, in the current application, employee update/delete/get-by-ID and all text-file operations are **not exposed as REST routes**, despite helper functions being present in the repository.

## Current setup details to check

The current `main.py` has its own `get_db()` function and its MySQL connection settings are hard-coded there. This means it does not use the environment-variable connection helper in `database.py`. Also compare its database name with `schema.sql`: the current main file names `employee_db`, while the schema file creates `employee_management`. The configured database and the schema must match for the routes to work. Do not share `.env` values, passwords, or other credentials in chat or commit them to Git.

## Built-in functions, types, and standard-library modules

“Built-in” can refer to Python built-in functions/types or to the standard library. These are different from third-party packages:

| Name | Category | Use in this project |
| --- | --- | --- |
| `str`, `int`, `dict`, `list`, `tuple` | Built-in types | Type annotations, request fields, and query parameter/result data |
| `None` | Built-in singleton value | Represents no returned employee when a lookup finds no row |
| `ValueError` | Built-in exception class | Used by the text file helper to report invalid filenames |
| `pass` | Language statement | Empty body used when creating an empty file |
| `try`, `except`, `finally`, `with` | Language statements | Handle cleanup/errors and manage files/resources where used |
| `pathlib.Path` | Standard-library class | Build and validate text-file paths |
| `shutil.copyfileobj` | Standard-library function | Copy file contents |
| `os` | Standard-library module | Read environment variables in `database.py` |
| `typing.Any` | Standard-library typing name | Used in type annotations in `employee_queries.py` |

Python's built-in types and the standard library ship with Python; they are not added to `requirements.txt`. `Path.open()`, `Path.read_text()`, and `Path.write_text()` are methods, not built-in functions.

## Third-party packages imported or declared

| Package/module | Source | Current project role |
| --- | --- | --- |
| `fastapi` | `fastapi` requirement | Defines the API app, routes, and request handling in `main.py` |
| `pydantic` | Imported by `main.py`; normally installed as a FastAPI dependency | `BaseModel` validates the employee request body |
| `mysql.connector` | `mysql-connector-python` requirement | Creates the MySQL connection and executes database operations |
| `uvicorn` | `uvicorn` requirement | Runs the application; invoked from the terminal rather than imported in `main.py` |
| `dotenv` | `python-dotenv` requirement | `database.py` loads `.env`; the current `main.py` connection helper does not use it |
| `python-multipart` | Declared in requirements | Enables multipart parsing for upload endpoints when implemented; it is not used by the current routes |

The HTTP routes implemented now do not include file uploads, CSV/JSON processing, or employee search.

## 30 interview questions and answers

1. **What is an API?**
   **Answer:** An API is a defined interface through which one program can request data or actions from another program. For a web API, the client sends an HTTP request and the server returns an HTTP status and often a JSON response. For example, Postman can send `GET /employees` and display the employee list.

2. **What does REST mean in a REST API?**
   **Answer:** REST is an architectural style for networked applications, not a programming language or Python package. A REST-style API commonly identifies resources with URLs and uses HTTP methods such as GET to read and POST to create. The project's `/employees` path represents the employee collection.

3. **What is an HTTP endpoint?**
   **Answer:** An endpoint is the combination of an HTTP method and a route path handled by a server. `GET /employees` and `POST /employees` use the same path but are different endpoints because they perform different actions. In FastAPI, route decorators connect endpoints to Python functions.

4. **What is FastAPI?**
   **Answer:** FastAPI is a Python framework for building HTTP APIs. It uses Python type annotations and Pydantic models to validate input, and it generates OpenAPI documentation that can be explored at `/docs`. In this project, `app = FastAPI(...)` creates the application object to which routes are attached.

5. **What does Uvicorn do?**
   **Answer:** Uvicorn is an ASGI server that runs the FastAPI application and accepts HTTP connections. FastAPI defines how requests are handled; Uvicorn serves that application over the network. The project starts it with `python -m uvicorn main:app --reload`.

6. **What does `main:app` mean in the Uvicorn command?**
   **Answer:** The part before the colon, `main`, identifies the Python module (`main.py`) to import. The part after the colon, `app`, is the variable in that module containing the FastAPI application. If either name is wrong or the module cannot be imported, Uvicorn cannot start the application.

7. **What does `--reload` do?**
   **Answer:** It watches the development project for source changes and restarts the server when files are saved. This makes local development convenient because you usually do not need to stop and restart Uvicorn manually. It is a development convenience and should not be used as the production process manager.

8. **What does `requirements.txt` contain?**
   **Answer:** It lists external Python packages the project needs, such as FastAPI and the MySQL connector. Pip reads the file when you run `python -m pip install -r requirements.txt`. This project's file lists direct packages but does not currently pin their versions, so installs may resolve to different compatible versions over time.

9. **What is a virtual environment?**
   **Answer:** It is an isolated Python environment for a project, with its own interpreter context and installed packages. Installing FastAPI into this project's `.venv` avoids unintentionally changing packages used by another project. Activate it before installing packages or running the application so commands use the intended environment.

10. **Why should `.venv` usually not be committed?**
    **Answer:** It contains locally installed interpreter and package files, which can be large and specific to an operating system or machine. Other developers should recreate it from the dependency manifest instead of downloading your local environment. This repository's `.gitignore` excludes `.venv`.

11. **What is Pydantic used for here?**
    **Answer:** Pydantic models describe the expected fields and types of request data. The current `Employee` model in `main.py` requires `name`, `email`, `department`, and integer `salary`; FastAPI validates an incoming POST body against that model before calling the route function. Missing or incorrectly typed fields typically produce a `422` response.

12. **What is JSON?**
    **Answer:** JSON is a text-based format for representing structured data using objects, arrays, strings, numbers, booleans, and null. The project accepts an employee as a JSON object and returns employee results as JSON. JSON keys and values must follow JSON syntax—for example, strings use double quotes.

13. **What is the purpose of `GET`?**
    **Answer:** GET requests data from a server and should not be used to change stored state. In this project, `GET /` returns a health-style message and `GET /employees` retrieves employee rows. A successful GET normally uses status `200 OK`.

14. **What is the purpose of `POST`?**
    **Answer:** POST submits data to a server for processing and is commonly used to create a resource. Here, `POST /employees` validates an employee body and inserts it into MySQL. The current route does not specify a custom status code, so FastAPI normally returns `200 OK`, even though many APIs choose `201 Created` for creation.

15. **What does `200 OK` mean?**
    **Answer:** It means the server successfully processed the request. The current GET routes use this success response, and the current POST route also defaults to 200 because no alternative status was configured. A 200 response can include a JSON body with the result.

16. **What does `201 Created` mean?**
    **Answer:** It indicates that the request successfully created a resource. An API commonly returns the new resource in the response and may provide its location. The current employee POST route does not explicitly set 201; it currently returns FastAPI's default `200 OK`.

17. **What does `422 Unprocessable Entity` usually indicate here?**
    **Answer:** It means the request reached the API but its body did not match the required input model. For example, omitting `salary`, sending a string where an integer is expected, or sending malformed field data can fail validation. Read the response JSON's `detail` field to see which field FastAPI rejected.

18. **Why should an API validate input?**
    **Answer:** Validation rejects missing, incorrectly typed, or otherwise unacceptable values before business logic or database operations use them. It gives the caller a clear error instead of allowing bad data to cause confusing downstream failures. Validation should be paired with database constraints because multiple applications may write to the same database.

19. **What is a database connection?**
    **Answer:** It is a communication session between the Python application and the database server. The application uses it to send SQL statements and receive results. Connections consume resources, so applications should close them after use or manage them with an appropriate connection-pooling strategy.

20. **What does a database cursor do?**
    **Answer:** A cursor executes SQL statements through a database connection and exposes query results. For example, a cursor can execute `SELECT * FROM employees` and fetch rows using a method such as `fetchall()`. Cursors should be closed when finished so database resources can be released.

21. **What does `commit()` do?**
    **Answer:** It asks the database to finalize the current transaction's changes, such as an INSERT or UPDATE. Without a commit, many database connections do not persist the changes when the connection closes. If an operation fails before commit, applications should handle the error and decide whether to roll the transaction back.

22. **Why use SQL placeholders such as `%s`?**
    **Answer:** Placeholders let the connector send SQL structure separately from the values supplied by the user. This helps the driver treat values as data rather than executable SQL and reduces SQL-injection risk. Do not build SQL by concatenating untrusted strings into the query.

23. **What is a primary key?**
    **Answer:** A primary key is a column, or combination of columns, that uniquely identifies each row in a table. In the schema file, `id` is the primary key and is configured to auto-increment. This lets API callers refer to an employee by a stable ID rather than by a name that might not be unique.

24. **What does a `UNIQUE` constraint do?**
    **Answer:** It tells the database to reject duplicate values for the constrained column or column combination. The project's schema marks employee email as unique so two rows cannot use the same email under MySQL's unique-index rules. Database constraints protect the data even if an application-level check is skipped.

25. **What is the purpose of `mysql-connector-python`?**
    **Answer:** It is the Python database driver used to communicate with MySQL. It provides connection and cursor objects, executes SQL statements, and returns query results. It is listed in `requirements.txt` under its installable package name and imported in Python as `mysql.connector`.

26. **Why store configuration outside source code?**
    **Answer:** Configuration can differ between a developer's computer, test environment, and deployment, while the application code remains the same. Keeping passwords out of source files also lowers the chance of accidentally publishing them. The current `main.py` connection values are hard-coded, so they should be moved to environment-based configuration before sharing or deploying the code.

27. **What is `python-dotenv` used for in this repository?**
    **Answer:** It provides `load_dotenv()`, which reads key/value pairs from a local `.env` file into process environment variables. The current `database.py` uses it before reading the database settings. The current `main.py` defines a separate database connection function and does not use that helper, so its connection still uses the values hard-coded there.

28. **What is a Python built-in module?**
    **Answer:** A built-in or standard-library module is functionality supplied with Python rather than installed as a separate project dependency. Examples used in this repository include `os`, `pathlib`, and `shutil`. They are imported in Python code but normally do not belong in `requirements.txt`.

29. **What is the difference between a helper function and an API route?**
    **Answer:** A helper function is ordinary Python code that other Python code can call. An API route is registered with FastAPI, usually using a decorator such as `@app.get(...)`, so an HTTP client can invoke it. The current `main.py` does not register the employee query or text-file helper functions as routes, so their presence in other files does not make them available over HTTP.

30. **What should you check when `GET /` returns 404?**
    **Answer:** Confirm the URL, port, running server, and module/application specified in the Uvicorn command. The current `main.py` shown in this guide defines `GET /` and returns `{"message": "API Working"}`, so a 404 means the request likely reached a different app/version or the current code was not the one served. Visit `/docs` on the same host and port to inspect the routes actually registered by the running server.
