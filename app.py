"""
TaskFlow AI - Smart Task Manager
A small full-stack project: Flask REST API + SQLite database + AI-assisted
priority suggestions + a simple web UI.

Run with:
    pip install -r requirements.txt
    python app.py
Then open http://127.0.0.1:5000 in your browser.
"""

from flask import Flask, jsonify, request, render_template
import sqlite3
import os

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), "tasks.db")


# ---------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            priority TEXT DEFAULT 'medium',
            done INTEGER DEFAULT 0
        )
        """
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------
# "AI Assistant" - suggests a priority for a task.
#
# This is a lightweight, rule-based stand-in for a real AI call so the
# project runs with zero API keys or cost. In a real AI-assisted
# workflow, you would replace the body of this function with a call to
# an LLM API (e.g. the Claude API) and ask it to classify the task.
# The function signature and the rest of the app would not need to
# change - that's the point of separating "what it does" (an interface)
# from "how it does it" (rule-based vs. AI-based).
# ---------------------------------------------------------------------
URGENT_WORDS = {"امروز", "فوری", "امتحان", "امتحان", "asap", "urgent", "today", "deadline", "ددلاین"}
LOW_WORDS = {"شاید", "بعدا", "بعداً", "someday", "later", "optional", "اختیاری"}


def suggest_priority(title: str, description: str) -> str:
    text = f"{title} {description}".lower()
    if any(word in text for word in URGENT_WORDS):
        return "high"
    if any(word in text for word in LOW_WORDS):
        return "low"
    return "medium"


# ---------------------------------------------------------------------
# Routes - Web UI
# ---------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


# ---------------------------------------------------------------------
# Routes - REST API
# ---------------------------------------------------------------------
@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    conn = get_db()
    tasks = conn.execute("SELECT * FROM tasks ORDER BY done ASC, id DESC").fetchall()
    conn.close()
    return jsonify([dict(t) for t in tasks])


@app.route("/api/tasks", methods=["POST"])
def create_task():
    data = request.get_json(force=True)
    title = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip()

    if not title:
        return jsonify({"error": "Title is required"}), 400

    priority = suggest_priority(title, description)

    conn = get_db()
    cur = conn.execute(
        "INSERT INTO tasks (title, description, priority) VALUES (?, ?, ?)",
        (title, description, priority),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()

    return jsonify({
        "id": new_id,
        "title": title,
        "description": description,
        "priority": priority,
        "done": 0,
    }), 201


@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json(force=True)
    conn = get_db()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if task is None:
        conn.close()
        return jsonify({"error": "Task not found"}), 404

    done = data.get("done", task["done"])
    title = data.get("title", task["title"])
    description = data.get("description", task["description"])
    priority = data.get("priority", task["priority"])

    conn.execute(
        "UPDATE tasks SET title=?, description=?, priority=?, done=? WHERE id=?",
        (title, description, priority, int(bool(done)), task_id),
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "updated"})


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    conn = get_db()
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "deleted"})


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
