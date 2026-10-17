"""Student Management System - Flask + SQLite backend."""
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, g

app = Flask(__name__)
app.secret_key = "change-this-secret-key"
DATABASE = "students.db"


# ---------- Database helpers ----------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    with sqlite3.connect(DATABASE) as db:
        db.execute(
            """CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                roll_no TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT,
                course TEXT NOT NULL,
                year INTEGER NOT NULL
            )"""
        )


def read_form():
    f = request.form
    return {
        "roll_no": f.get("roll_no", "").strip(),
        "name": f.get("name", "").strip(),
        "email": f.get("email", "").strip(),
        "phone": f.get("phone", "").strip(),
        "course": f.get("course", "").strip(),
        "year": f.get("year", "").strip(),
    }


def validate(data):
    if not all([data["roll_no"], data["name"], data["email"], data["course"], data["year"]]):
        return "Fill in roll number, name, email, course and year."
    if "@" not in data["email"]:
        return "Enter a valid email address."
    if not data["year"].isdigit() or not 1 <= int(data["year"]) <= 6:
        return "Year must be a number from 1 to 6."
    if data["phone"] and not data["phone"].replace("+", "").replace(" ", "").isdigit():
        return "Phone number can only contain digits, spaces and +."
    return None


# ---------- Routes ----------
@app.route("/")
def index():
    q = request.args.get("q", "").strip()
    db = get_db()
    if q:
        like = f"%{q}%"
        students = db.execute(
            "SELECT * FROM students WHERE name LIKE ? OR roll_no LIKE ? OR course LIKE ? ORDER BY name",
            (like, like, like),
        ).fetchall()
    else:
        students = db.execute("SELECT * FROM students ORDER BY name").fetchall()
    total = db.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    courses = db.execute("SELECT COUNT(DISTINCT course) FROM students").fetchone()[0]
    return render_template("index.html", students=students, q=q, total=total, courses=courses)


@app.route("/add", methods=["GET", "POST"])
def add():
    data = {k: "" for k in ("roll_no", "name", "email", "phone", "course", "year")}
    if request.method == "POST":
        data = read_form()
        error = validate(data)
        if error:
            flash(error, "error")
        else:
            try:
                get_db().execute(
                    "INSERT INTO students (roll_no, name, email, phone, course, year) VALUES (?,?,?,?,?,?)",
                    (data["roll_no"], data["name"], data["email"], data["phone"], data["course"], int(data["year"])),
                )
                get_db().commit()
                flash(f"{data['name']} was added.", "success")
                return redirect(url_for("index"))
            except sqlite3.IntegrityError:
                flash("A student with this roll number already exists.", "error")
    return render_template("form.html", student=data, mode="add")


@app.route("/edit/<int:student_id>", methods=["GET", "POST"])
def edit(student_id):
    db = get_db()
    student = db.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    if student is None:
        flash("Student not found.", "error")
        return redirect(url_for("index"))
    if request.method == "POST":
        data = read_form()
        error = validate(data)
        if error:
            flash(error, "error")
            student = data
        else:
            try:
                db.execute(
                    "UPDATE students SET roll_no=?, name=?, email=?, phone=?, course=?, year=? WHERE id=?",
                    (data["roll_no"], data["name"], data["email"], data["phone"], data["course"], int(data["year"]), student_id),
                )
                db.commit()
                flash(f"{data['name']} was updated.", "success")
                return redirect(url_for("index"))
            except sqlite3.IntegrityError:
                flash("Another student already uses this roll number.", "error")
                student = data
    return render_template("form.html", student=student, mode="edit", student_id=student_id)


@app.route("/delete/<int:student_id>", methods=["POST"])
def delete(student_id):
    db = get_db()
    db.execute("DELETE FROM students WHERE id = ?", (student_id,))
    db.commit()
    flash("Student deleted.", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
