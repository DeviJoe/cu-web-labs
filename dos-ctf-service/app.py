import re
import time

from flask import Flask, render_template_string, request

app = Flask(__name__)

FLAG = "centralctf{r3g3x_d0s_1s_d4ng3r0us_4f73r_4ll}"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Email Validator Service</title>
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
        form {
            margin-top: 20px;
        }
        input[type="text"] {
            width: 100%;
            padding: 10px;
            font-size: 16px;
            border: 1px solid #ddd;
            border-radius: 5px;
            box-sizing: border-box;
        }
        button {
            margin-top: 10px;
            padding: 10px 20px;
            font-size: 16px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover {
            background-color: #0056b3;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            border-radius: 5px;
        }
        .success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .error {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .info {
            margin-top: 30px;
            padding: 15px;
            background-color: #e7f3ff;
            border-left: 4px solid #2196F3;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Email Validator Service</h1>
        <p>Enter your email address to validate its format:</p>

        <form method="POST" action="/validate">
            <input type="text" name="email" placeholder="Enter email address" required>
            <button type="submit">Validate Email</button>
        </form>

        {% if result %}
        <div class="result {{ result_class }}">
            {{ result }}
        </div>
        {% endif %}

        <div class="info">
            <h3>About this service</h3>
            <p>This is a simple email validation service that checks if your email format is correct.</p>
            <p>Processing time: {{ processing_time }} seconds</p>
        </div>
    </div>
</body>
</html>
"""


def validate_email(email):
    # Vulnerable regex pattern - ReDoS vulnerability
    pattern = r"^([a-zA-Z0-9]+)*@([a-zA-Z0-9]+)*\.([a-zA-Z]{2,})+$"

    start_time = time.time()
    match = re.match(pattern, email)
    end_time = time.time()

    processing_time = end_time - start_time

    if processing_time > 5:
        return True, processing_time, FLAG

    return match is not None, processing_time, None


@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE, result=None, processing_time=0)


@app.route("/validate", methods=["POST"])
def validate():
    email = request.form.get("email", "")

    is_valid, processing_time, flag = validate_email(email)

    if flag:
        result = f"Congratulations! You found the vulnerability! Flag: {flag}"
        result_class = "success"
    elif is_valid:
        result = "✓ Valid email format"
        result_class = "success"
    else:
        result = "✗ Invalid email format"
        result_class = "error"

    return render_template_string(
        HTML_TEMPLATE,
        result=result,
        result_class=result_class,
        processing_time=round(processing_time, 4),
    )


@app.route("/health")
def health():
    return {"status": "ok"}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
