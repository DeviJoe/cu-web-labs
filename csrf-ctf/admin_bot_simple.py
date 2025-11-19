import time

import requests

DATABASE = "/tmp/users.db"


def visit_url(url):
    """Admin bot visits the reported URL using requests"""
    try:
        # Create a session to maintain cookies
        session = requests.Session()

        # Login as admin
        login_data = {"username": "admin", "password": "admin_secret_password_123"}

        login_response = session.post(
            "http://localhost:5000/login",
            data=login_data,
            timeout=10,
            allow_redirects=True,
        )

        if login_response.status_code == 200:
            # Wait a bit
            time.sleep(1)

            # Visit the reported URL
            # This will execute any forms or requests on that page
            visit_response = session.get(url, timeout=10, allow_redirects=True)

            # If the URL contains a form that auto-submits, we might need to follow redirects
            time.sleep(2)

            print(f"Admin bot visited: {url} (Status: {visit_response.status_code})")
        else:
            print(f"Admin bot failed to login: {login_response.status_code}")

    except Exception as e:
        print(f"Admin bot error: {e}")
    finally:
        try:
            session.close()
        except:
            pass
