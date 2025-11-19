import hashlib
import os
import secrets
import sqlite3
from datetime import datetime

from flask import Flask, jsonify, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

DATABASE = "/tmp/users.db"
FLAG = os.environ.get("FLAG", "centralctf{csrf_1s_n0t_d3ad_yet}")


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            bio TEXT DEFAULT '',
            website TEXT DEFAULT '',
            is_admin INTEGER DEFAULT 0
        )
    """)

    # Create admin user with flag in bio
    admin_password = hashlib.sha256("admin_secret_password_123".encode()).hexdigest()
    try:
        conn.execute(
            "INSERT INTO users (username, password, bio, is_admin) VALUES (?, ?, ?, ?)",
            ("admin", admin_password, FLAG, 1),
        )
    except sqlite3.IntegrityError:
        pass

    conn.commit()
    conn.close()


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("profile"))
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return render_template("register.html", error="All fields are required")

        password_hash = hashlib.sha256(password.encode()).hexdigest()

        try:
            conn = get_db()
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password_hash),
            )
            conn.commit()
            conn.close()
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            return render_template("register.html", error="Username already exists")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        password_hash = hashlib.sha256(password.encode()).hexdigest()

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password_hash),
        ).fetchone()
        conn.close()

        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["is_admin"] = user["is_admin"]
            return redirect(url_for("profile"))
        else:
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE id = ?", (session["user_id"],)
    ).fetchone()
    conn.close()

    return render_template("profile.html", user=user)


@app.route("/update_profile", methods=["POST"])
def update_profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    bio = request.form.get("bio", "")
    website = request.form.get("website", "")

    conn = get_db()
    conn.execute(
        "UPDATE users SET bio = ?, website = ? WHERE id = ?",
        (bio, website, session["user_id"]),
    )
    conn.commit()
    conn.close()

    return redirect(url_for("profile"))


@app.route("/report", methods=["GET", "POST"])
def report():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        url = request.form.get("url")
        if url:
            # Simulate admin visiting the URL
            try:
                from admin_bot_simple import visit_url

                visit_url(url)
            except ImportError:
                try:
                    from admin_bot_playwright import visit_url_sync

                    visit_url_sync(url)
                except ImportError:
                    try:
                        from admin_bot import visit_url

                        visit_url(url)
                    except Exception as e:
                        print(f"Error importing admin bot: {e}")
                        pass
            return render_template(
                "report.html", success="Admin will check your link shortly"
            )

    return render_template("report.html")


@app.route("/users")
def users():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    all_users = conn.execute(
        "SELECT id, username, website FROM users WHERE is_admin = 0"
    ).fetchall()
    conn.close()

    return render_template("users.html", users=all_users)


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)
