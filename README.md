# Rest-API-using-python-and-MySQL

## Stage 3: Create the MySQL database

Run the SQL statements in [schema.sql](./schema.sql) using MySQL Workbench or the MySQL command-line client. The script creates the `employee_management` database and the `employees` table.

To verify the table in MySQL, run:

```sql
USE employee_management;
DESCRIBE employees;
```

## Stage 4: Connect Python to MySQL

In PowerShell, copy `.env.example` to `.env`, then replace the username and password in `.env` with your local MySQL credentials:

```powershell
Copy-Item .env.example .env
```

Keep `.env` private; it is excluded by `.gitignore`.

The `get_connection()` function in `database.py` reads those settings and opens a MySQL connection. It raises a clear `ValueError` if a required setting is missing and lets MySQL Connector errors surface if the server refuses the connection.

After installing the packages in `requirements.txt`, test the connection from the project folder with:

```powershell
python -c "from database import get_connection; connection = get_connection(); print('Connected to MySQL'); connection.close()"
```

The expected output is `Connected to MySQL`. If the connection fails, check that MySQL Server is running and that the values in your local `.env` file are correct.

## Stage 5: Implement employee CRUD APIs

`employee_queries.py` contains the SQL functions, and `main.py` defines the FastAPI routes and checks request data. Start the API from the project folder with the virtual environment active:

```powershell
python -m uvicorn main:app --reload
```

Open `http://127.0.0.1:8000/docs` to try the endpoints interactively. Every API request that reads or changes employee data requires the MySQL server and `employee_management` database to be available.

### Endpoints

| Method | URL | Purpose | Success |
| --- | --- | --- | --- |
| POST | `/employees` | Add an employee | `201 Created` |
| GET | `/employees` | Get all employees | `200 OK` |
| GET | `/employees/{employee_id}` | Get one employee | `200 OK` |
| PUT | `/employees/{employee_id}` | Replace all employee details | `200 OK` |
| DELETE | `/employees/{employee_id}` | Delete an employee | `200 OK` |

POST and PUT require a JSON body containing all four fields:

```json
{
  "name": "Asha Patel",
  "email": "asha@example.com",
  "department": "Engineering",
  "salary": 65000.00
}
```

For example, a successful POST returns the employee including its generated ID:

```json
{
  "id": 1,
  "name": "Asha Patel",
  "email": "asha@example.com",
  "department": "Engineering",
  "salary": 65000.0
}
```

The API rejects missing, unexpected, or invalid fields with `422`; a duplicate email returns `409`; and an unknown employee ID returns `404`. Database connector errors are logged and return `503`. SQL values are passed using `%s` placeholders rather than joined into SQL text, so the database treats user input as data.

### How the code works

- `main.py` starts the FastAPI app, validates employee JSON, calls the query functions, and turns expected errors into HTTP responses.
- `employee_queries.py` executes parameterized SQL. Each function closes its cursor and connection in `finally`, including when a query fails; write functions call `commit()` to save their changes.
- `database.py` reads local settings and creates a database connection.
- `schema.sql` creates the database and table that the queries use.
- `requirements.txt` lists the external Python packages.
- `.env` contains local database settings and must remain private; `.env.example` is a safe template.
- `uploads/` and `reports/` will be used in later file-handling stages.

### Common errors

- **`503 Database operation failed`:** Check that MySQL is running, `.env` settings are correct, and Stage 3's database exists.
- **`409` when creating or updating:** That email is already in use; choose a unique email.
- **`422` response:** Check that the request is valid JSON and has exactly `name`, `email`, `department`, and numeric, non-negative `salary`.
- **`404 Employee not found`:** Check the ID and confirm the record has not been deleted.
- **Uvicorn cannot import `main`:** Run the command from the project folder and verify the `.venv` interpreter is active.

### Interview questions

1. **What does CRUD stand for?** Create, Read, Update, and Delete.
2. **Why use SQL placeholders such as `%s`?** They pass values separately from SQL syntax, preventing input from changing the structure of a query.
3. **What does `commit()` do?** It saves a transaction's changes to the database.
4. **Why close a cursor and connection in `finally`?** The `finally` block runs even when a query raises an error, so resources are released.
5. **Why return `404` for an unknown employee ID?** It communicates that the requested resource does not exist.

### Practice tasks

1. Use `/docs` to create an employee, list employees, then retrieve that employee by ID.
2. Try creating the same email twice and retrieving a nonexistent ID. Observe the `409` and `404` responses.

## Stage 6: Test the API with Postman

Start the API and confirm MySQL is running before testing. In Postman, import [employee_api.postman_collection.json](./postman/employee_api.postman_collection.json) by selecting **Import** and choosing the file. The collection sends requests to `http://127.0.0.1:8000`.

Run the requests in this order:

1. **Create employee** — expects `201`. Postman creates a unique test email and saves the returned employee ID and email in collection variables.
2. **Get all employees** — expects `200` and a JSON array.
3. **Get employee by ID** — expects `200` and checks that the returned ID matches the created employee.
4. **Update employee** — expects `200`; changes the department to `Operations`.
5. **Delete employee** — expects `200` and removes the test record.

After each request, Postman's **Test Results** tab should show that its status check passed. Run **Create employee** first so Postman has an ID for the later requests. The collection deletes the test record at the end; do not run these requests against a database containing records you need to preserve unless you understand that they create and delete data.

To manually test errors, send a second POST with the same email as an existing employee and expect `409`. A GET for `/employees/999999` should return `404` unless that ID actually exists. A POST with a missing field or negative salary should return `422`. These error tests require an available database except for malformed request bodies rejected by FastAPI.

If requests fail, check that Uvicorn is still running, the URL uses port `8000`, and the MySQL service and `.env` settings are correct. Postman does not require an API key for this beginner project.

### Stage 6 interview questions

1. **What does Postman do?** It sends HTTP requests to an API and displays the status code, headers, and response body.
2. **What does `201 Created` mean?** The server successfully created a resource.
3. **What is the difference between `PUT` and `GET` here?** `GET` reads employee data; `PUT` replaces the employee's supplied details.
4. **What does a response status code tell you?** It summarizes whether the request succeeded or why it failed.
5. **Why delete the test employee after testing?** It keeps test data from unnecessarily accumulating in the database.

### Stage 6 practice tasks

1. Import the collection and run the requests in the listed order. Note each response code.
2. Send a request for a nonexistent employee and a request with a negative salary. Compare the response bodies and status codes.

## Stage 7: Text-file operations

Text files are restricted to the project's `uploads/text/` folder. The API accepts simple `.txt` filenames only; it does not accept folder paths or arbitrary paths. The folder is created automatically when a text-file operation first needs it.

Start Uvicorn using the Stage 5 command. These routes can be tried in `/docs` or Postman:

| Method | URL | Purpose |
| --- | --- | --- |
| POST | `/files/text/{filename}` | Create an empty text file; returns `201` |
| PUT | `/files/text/{filename}` | Write or replace its content |
| POST | `/files/text/{filename}/append` | Append content (creates the file if absent) |
| GET | `/files/text/{filename}` | Read all content |
| GET | `/files/text/{filename}/lines` | Read as a list of lines |
| GET | `/files/text/{filename}/exists` | Check whether it exists |
| POST | `/files/text/{filename}/rename` | Rename within the text folder |
| POST | `/files/text/{filename}/copy` | Copy within the text folder |
| DELETE | `/files/text/{filename}` | Delete it |
| GET | `/files/text/{filename}/size` | Get its size in bytes |

For PUT and append, use a JSON body such as:

```json
{
  "content": "First line\nSecond line\n"
}
```

The rename body is `{"new_filename": "notes-renamed.txt"}` and the copy body is `{"copy_filename": "notes-copy.txt"}`. For example, create `notes.txt` with `POST /files/text/notes.txt`, write content with `PUT /files/text/notes.txt`, then read it with `GET /files/text/notes.txt`.

`file_operations.py` contains ordinary Python `pathlib` and `shutil` operations. `main.py` connects these functions to HTTP routes and returns useful status codes: `404` for a missing source, `409` when create/copy/rename would collide with an existing destination, `422` for invalid filenames or bodies, `403` for permission errors, and `500` for other filesystem failures. Create uses exclusive mode (`x`) so it will not silently overwrite a file; write replaces its contents; append adds to the end. Paths are resolved and checked to stay inside the project's text folder.

To try the operations, create and read a sample text file, append a line, read the lines and size, make a copy, rename the original, then delete the sample and copy. Avoid using files that contain information you want to keep.

### Stage 7 interview questions

1. **What does `Path.read_text()` do?** It reads a text file and returns its contents as a string.
2. **What is the difference between write mode and append mode?** Write mode replaces file content; append mode adds content at the end.
3. **Why use UTF-8 when opening text files?** It provides a standard encoding for a wide range of characters.
4. **Why restrict file paths to a designated folder?** It prevents API callers from accessing files elsewhere on the computer.
5. **What does file size in bytes measure?** The amount of storage occupied by the file, not necessarily its number of characters.

### Stage 7 practice tasks

1. Create `practice.txt`, write two lines, append a third, and compare the full-file response with the lines response.
2. Copy and rename the sample, check its byte size, then delete the test files. Try a path such as `../secret.txt` and observe the validation error.