from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from pathlib import Path

app = Flask(__name__)
DATABASE = "notes.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            category TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def categorize_note(content):
    text = content.lower().strip()

    study_keywords = [
        "study", "learn", "python", "flask", "code", "coding",
        "programming", "exam", "homework", "project", "university"
    ]
    work_keywords = [
        "work", "job", "meeting", "client", "task", "email",
        "office", "report", "deadline"
    ]

    if any(word in text for word in study_keywords):
        return "Study"
    if any(word in text for word in work_keywords):
        return "Work"
    return "General"


@app.route("/")
def index():
    conn = get_db()
    notes = conn.execute("""
        SELECT id, content, category, created_at
        FROM notes
        ORDER BY id DESC
    """).fetchall()
    conn.close()
    return render_template("index.html", notes=notes)


@app.route("/add", methods=["POST"])
def add():
    content = request.form.get("content", "").strip()

    if not content:
        return redirect(url_for("index"))

    category = categorize_note(content)

    conn = get_db()
    conn.execute(
        "INSERT INTO notes (content, category) VALUES (?, ?)",
        (content, category)
    )
    conn.commit()
    conn.close()

    return redirect(url_for("index"))


@app.route("/delete/<int:note_id>", methods=["POST"])
def delete(note_id):
    conn = get_db()
    conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()

    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)