import os

from flask import Flask, redirect, render_template_string, request, url_for

app = Flask(__name__)

# Секретный флаг
FLAG = os.environ.get("FLAG", "centralctf{t3mpl4t3_1nj3ct10n_1s_d4ng3r0us}")

# Простая база данных пользователей
users = {
    "admin": {"password": "super_secret_admin_pass_12345", "role": "admin"},
    "guest": {"password": "guest123", "role": "user"},
}


@app.route("/")
def index():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Student Portal</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background-color: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
            }
            .menu {
                margin: 20px 0;
            }
            .menu a {
                display: inline-block;
                margin: 10px 10px 10px 0;
                padding: 10px 20px;
                background-color: #007bff;
                color: white;
                text-decoration: none;
                border-radius: 5px;
            }
            .menu a:hover {
                background-color: #0056b3;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Welcome to Student Portal</h1>
            <p>A simple web application for students</p>
            <div class="menu">
                <a href="/login">Login</a>
                <a href="/search">Search</a>
                <a href="/about">About</a>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if username in users and users[username]["password"] == password:
            return redirect(url_for("dashboard", user=username))
        else:
            error = "Invalid credentials"
            html = (
                """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Login - Student Portal</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        max-width: 400px;
                        margin: 50px auto;
                        padding: 20px;
                    }
                    .container {
                        background-color: white;
                        padding: 30px;
                        border-radius: 10px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }
                    input {
                        width: 100%;
                        padding: 10px;
                        margin: 10px 0;
                        box-sizing: border-box;
                    }
                    button {
                        width: 100%;
                        padding: 10px;
                        background-color: #007bff;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        cursor: pointer;
                    }
                    .error {
                        color: red;
                        margin: 10px 0;
                    }
                    a {
                        color: #007bff;
                        text-decoration: none;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>Login</h2>
                    <div class="error">"""
                + error
                + """</div>
                    <form method="POST">
                        <input type="text" name="username" placeholder="Username" required>
                        <input type="password" name="password" placeholder="Password" required>
                        <button type="submit">Login</button>
                    </form>
                    <p><a href="/">Back to Home</a></p>
                </div>
            </body>
            </html>
            """
            )
            return render_template_string(html)

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login - Student Portal</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 400px;
                margin: 50px auto;
                padding: 20px;
            }
            .container {
                background-color: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            input {
                width: 100%;
                padding: 10px;
                margin: 10px 0;
                box-sizing: border-box;
            }
            button {
                width: 100%;
                padding: 10px;
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }
            a {
                color: #007bff;
                text-decoration: none;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Login</h2>
            <form method="POST">
                <input type="text" name="username" placeholder="Username" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Login</button>
            </form>
            <p><a href="/">Back to Home</a></p>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)


@app.route("/dashboard")
def dashboard():
    user = request.args.get("user", "Guest")
    html = (
        """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard - Student Portal</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
            }
            .container {
                background-color: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            a {
                color: #007bff;
                text-decoration: none;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Welcome, """
        + user
        + """!</h2>
            <p>You have successfully logged in.</p>
            <p><a href="/">Back to Home</a></p>
        </div>
    </body>
    </html>
    """
    )
    return render_template_string(html)


@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        query = request.form.get("query", "")
        # SSTI уязвимость здесь
        result_html = (
            '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Search Results - Student Portal</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 50px auto;
                    padding: 20px;
                }
                .container {
                    background-color: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                .result {
                    background-color: #f8f9fa;
                    padding: 15px;
                    margin: 15px 0;
                    border-radius: 5px;
                }
                a {
                    color: #007bff;
                    text-decoration: none;
                }
                form {
                    margin: 20px 0;
                }
                input[type="text"] {
                    width: 70%;
                    padding: 10px;
                    margin-right: 10px;
                }
                button {
                    padding: 10px 20px;
                    background-color: #007bff;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Search Results</h2>
                <form method="POST">
                    <input type="text" name="query" placeholder="Search..." value="'''
            + query
            + """">
                    <button type="submit">Search</button>
                </form>
                <div class="result">
                    <p>You searched for: """
            + query
            + """</p>
                </div>
                <p><a href="/">Back to Home</a></p>
            </div>
        </body>
        </html>
        """
        )
        return render_template_string(result_html)

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Search - Student Portal</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
            }
            .container {
                background-color: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            input[type="text"] {
                width: 70%;
                padding: 10px;
                margin-right: 10px;
            }
            button {
                padding: 10px 20px;
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }
            a {
                color: #007bff;
                text-decoration: none;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Search</h2>
            <form method="POST">
                <input type="text" name="query" placeholder="Search..." required>
                <button type="submit">Search</button>
            </form>
            <p><a href="/">Back to Home</a></p>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)


@app.route("/about")
def about():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>About - Student Portal</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
            }
            .container {
                background-color: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            a {
                color: #007bff;
                text-decoration: none;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>About Student Portal</h2>
            <p>This is a simple web application built with Flask.</p>
            <p>Version: 1.0.0</p>
            <p><a href="/">Back to Home</a></p>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
