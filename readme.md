


# Smart Task Analyzer – Assessment Project

This project was built for the **Singularium Internship Assessment 2025**.  
It provides a lightweight system that analyzes tasks, assigns priority scores, and suggests which tasks to work on next.

The solution contains:
- A **Django + Django REST Framework** backend (API + scoring engine)
- A **simple frontend** (HTML, CSS, JavaScript)
- Unit tests for API behavior

---

## Features

- Add tasks manually or paste bulk JSON
- Choose between priority strategies:
  - Smart Balance (default)
  - Fastest Wins
  - High Impact
  - Deadline Driven
- Analyze tasks to get:
  - A numeric priority score (0–1)
  - Human-readable explanation for each score
  - Sorted list of tasks by priority
- Suggest the top 3 tasks to work on next
- Detect and warn about circular dependencies

---

## How the Scoring Works (high level)

Each task receives a score between **0** and **1** based on a blend of:

- **Urgency** — how soon the task is due (past-due tasks get a boost)
- **Importance** — a user-supplied value from 1–10
- **Effort** — estimated hours; smaller tasks get a small “quick-win” boost
- **Dependencies** — tasks that block other tasks get higher priority

The algorithm is intentionally simple and explainable. Different strategy presets adjust the relative weights of these factors.

---

## Project Structure

```

task-analyzer/
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── task_analyzer/      # Django project
│   └── tasks/              # Django app with scoring, views, tests
└── frontend/
├── index.html
├── script.js
└── styles.css

````

---

## Setup & Run (Backend)

1. Open a terminal and go to the backend folder:
   ```bash
   cd backend


2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   # mac / linux
   source .venv/bin/activate
   # windows (PowerShell)
   .\.venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run database migrations:

   ```bash
   python manage.py migrate
   ```

5. Start the development server:

   ```bash
   python manage.py runserver
   ```

The API will be available at `http://127.0.0.1:8000`.

---

## Frontend

* Open `frontend/index.html` in your browser to use the UI.
* Optionally, move frontend files into Django static folder and open:
  `http://127.0.0.1:8000/static/index.html`

---

## API Endpoints

### `POST /api/tasks/analyze/`

* Input: JSON array of tasks (or a JSON object with `tasks: [...]`)
* Each task expected fields (recommended):

  ```json
  {
    "id": "1",
    "title": "Fix login",
    "due_date": "2025-11-30",
    "estimated_hours": 3,
    "importance": 8,
    "dependencies": ["2", "3"]
  }
  ```
* Response: array of tasks with `score` and `reason`, plus `meta` (e.g., cycle detection)

### `POST /api/tasks/suggest/`

* Input: same as analyze
* Response: top 3 suggestions with explanations

---

## Running Tests

From the `backend` folder:

```bash
python manage.py test tasks
```

Tests cover:

* Basic scoring and sorting
* Suggest endpoint behavior
* Invalid input handling

---

## Design Notes & Decisions

* The scoring formula is explainable and bounded (0–1)
* Urgency uses a fixed horizon so tasks due very far in the future don't dominate
* Effort uses an inverse curve to reward quick wins without letting tiny tasks dominate
* Dependencies are counted as "blocking" weight — a task that unblocks many tasks is more important
* Circular dependency detection prevents incorrect prioritization and informs the user
* Strategy presets let the user trade off speed vs impact vs deadlines

---

## Known Limitations & Future Work

* No user accounts or persistent task lists (optional enhancement)
* A richer UI (drag-and-drop, graphs) would improve usability
* Allow users to tune weights manually in the UI
* Add persistent storage and multi-user support for production

---

## Final Notes

This project is intended to be clear, testable, and easy to run locally.
If you'd like, I can also provide:

* A short repo description for GitHub
* Example `curl` requests and sample payloads
* A 60-second script to explain the project in interviews

Thanks for checking out the Smart Task Analyzer!

