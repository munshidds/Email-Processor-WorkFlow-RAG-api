## Simple Student Management System (FastAPI + Vanilla JS)

This is a minimal **student management system** built with **FastAPI** on the backend and **plain HTML/CSS/JavaScript** on the frontend.

You can **create, list, update, and delete** students, all stored in an in-memory list (no database).

### 1. Install dependencies

From `/home/dev/Azure_learning`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Run the FastAPI server

```bash
uvicorn main:app --reload
```

By default the API will be available at:

- **API root**: `http://127.0.0.1:8000`
- **OpenAPI docs**: `http://127.0.0.1:8000/docs`

### 3. Open the frontend

The static files are in the `static` folder.

You can open `static/index.html` directly in your browser (e.g. double-click the file or use `file:///` path).  
The JavaScript in `script.js` calls the API at `http://127.0.0.1:8000/api/...`, so make sure **Uvicorn is running**.

### 4. API endpoints (summary)

- **GET** `/api/students` – list all students
- **POST** `/api/students` – create a new student  
  Body JSON:

  ```json
  {
    "name": "Alice",
    "age": 20,
    "grade": "A"
  }
  ```

- **PUT** `/api/students/{id}` – update an existing student
- **DELETE** `/api/students/{id}` – delete a student

All data is stored in memory, so it resets whenever you restart the server.


