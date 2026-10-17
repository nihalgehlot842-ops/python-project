# Student Management System (Flask mini project)

Frontend: HTML + CSS (Jinja2 templates)  |  Backend: Python Flask  |  Database: SQLite

## Features
- Add, view, edit and delete students
- Search by name, roll number or course
- Form validation and duplicate roll number check
- Summary of total students and courses

## Run
    pip install -r requirements.txt
    python app.py
Open http://127.0.0.1:5000

## Structure
    student_management/
    ├── app.py              # routes + database logic
    ├── requirements.txt
    ├── students.db         # created automatically on first run
    ├── templates/          # base.html, index.html, form.html
    └── static/style.css
