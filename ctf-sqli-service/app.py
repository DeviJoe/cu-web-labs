import re
import sqlite3
import sys

from flask import Flask, g, render_template, request

app = Flask(__name__)
DATABASE = "ctf.db"


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()

        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                email TEXT NOT NULL
            )
        """)

        # Create secrets table with flag
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS secrets (
                id INTEGER PRIMARY KEY,
                secret_key TEXT NOT NULL,
                secret_value TEXT NOT NULL
            )
        """)

        # Insert sample users
        cursor.execute("DELETE FROM users")
        users = [
            (1, "alice", "alice@example.com"),
            (2, "bob", "bob@example.com"),
            (3, "charlie", "charlie@example.com"),
            (4, "david", "david@example.com"),
        ]
        cursor.executemany("INSERT INTO users VALUES (?, ?, ?)", users)

        # Insert flag
        cursor.execute("DELETE FROM secrets")
        cursor.execute("""
            INSERT INTO secrets (id, secret_key, secret_value)
            VALUES (1, 'flag', 'centralctf{bl1nd_5ql_w1th_w4f_byp4ss_m4st3r}')
        """)

        db.commit()


def waf_check(query_string):
    """Simple WAF to block common SQL injection patterns"""
    dangerous_patterns = [
        r"\bselect\b",
        r"\bunion\b",
        r"\bor\b",
        r"\band\b",
        r"\bwhere\b",
        r"\bfrom\b",
        r"\binsert\b",
        r"\bdelete\b",
        r"\bdrop\b",
        r"\bupdate\b",
        r"\b0x[0-9a-f]+\b",
        r"--",
        r"/\*",
        r"\*/",
        r"@@",
        r"char\(",
        r"concat\(",
        r"group_concat\(",
    ]

    query_lower = query_string.lower()

    for pattern in dangerous_patterns:
        if re.search(pattern, query_lower):
            return True

    return False


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search")
def search():
    # Get the raw query string to check WAF BEFORE Flask decodes it
    raw_query = request.query_string.decode("utf-8")

    # Extract id parameter value from raw query string
    user_id = request.args.get("id", "")

    # Debug logging
    print(f"[DEBUG] Raw query: {raw_query}", file=sys.stderr)
    print(f"[DEBUG] Decoded user_id: {user_id}", file=sys.stderr)

    if not user_id:
        return render_template("search.html", error="Please provide a user ID")

    # WAF check on RAW query string (before URL decoding)
    # This allows bypass via URL encoding because WAF checks encoded version
    # but SQL uses decoded version
    waf_result = waf_check(raw_query)
    print(f"[DEBUG] WAF check result: {waf_result}", file=sys.stderr)

    if waf_result:
        return render_template(
            "search.html", error="Malicious input detected! Access denied."
        )

    # Flask already decoded the parameter, so user_id contains decoded value
    # This is the vulnerability - decoded value goes into SQL query

    # Vulnerable query - Blind SQL Injection
    db = get_db()
    cursor = db.cursor()

    try:
        # Intentionally vulnerable query
        query = f"SELECT username, email FROM users WHERE id = {user_id}"
        cursor.execute(query)
        result = cursor.fetchone()

        if result:
            # Blind SQLi - only returns True/False, no data leakage
            return render_template("search.html", success=True, found=True)
        else:
            return render_template("search.html", success=True, found=False)
    except Exception as e:
        # Don't leak error information
        return render_template("search.html", success=True, found=False)


@app.route("/health")
def health():
    return "OK", 200


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5050, debug=False)
