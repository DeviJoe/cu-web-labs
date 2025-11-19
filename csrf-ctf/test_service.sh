#!/bin/bash

# CSRF CTF Service Test Script
# This script verifies that the service is working correctly

set -e

BASE_URL="http://localhost:5000"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "CSRF CTF Service Test"
echo "=========================================="
echo ""

# Test 1: Check if service is running
echo -n "Test 1: Checking if service is accessible... "
if curl -s -o /dev/null -w "%{http_code}" "$BASE_URL" | grep -q "200"; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
    echo "Service is not running on $BASE_URL"
    exit 1
fi

# Test 2: Check homepage content
echo -n "Test 2: Checking homepage content... "
if curl -s "$BASE_URL" | grep -q "Profile Manager"; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
    exit 1
fi

# Test 3: Register a new user
echo -n "Test 3: Testing user registration... "
RANDOM_USER="testuser_$$_$RANDOM"
REGISTER_RESPONSE=$(curl -s -w "%{http_code}" -o /tmp/register_response.html \
    -X POST "$BASE_URL/register" \
    -d "username=$RANDOM_USER&password=testpass123")

if echo "$REGISTER_RESPONSE" | grep -q "200\|302"; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
    exit 1
fi

# Test 4: Login with created user
echo -n "Test 4: Testing user login... "
LOGIN_RESPONSE=$(curl -s -c /tmp/cookies.txt -w "%{http_code}" -o /tmp/login_response.html \
    -X POST "$BASE_URL/login" \
    -d "username=$RANDOM_USER&password=testpass123")

if echo "$LOGIN_RESPONSE" | grep -q "200\|302"; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
    exit 1
fi

# Test 5: Access profile page
echo -n "Test 5: Testing profile access... "
PROFILE_RESPONSE=$(curl -s -b /tmp/cookies.txt "$BASE_URL/profile")
if echo "$PROFILE_RESPONSE" | grep -q "My Profile"; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
    exit 1
fi

# Test 6: Update profile (CSRF vulnerable endpoint)
echo -n "Test 6: Testing profile update (vulnerable endpoint)... "
UPDATE_RESPONSE=$(curl -s -b /tmp/cookies.txt -w "%{http_code}" -o /tmp/update_response.html \
    -X POST "$BASE_URL/update_profile" \
    -d "bio=Test bio&website=http://example.com")

if echo "$UPDATE_RESPONSE" | grep -q "200\|302"; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
    exit 1
fi

# Test 7: Verify profile was updated
echo -n "Test 7: Verifying profile update... "
UPDATED_PROFILE=$(curl -s -b /tmp/cookies.txt "$BASE_URL/profile")
if echo "$UPDATED_PROFILE" | grep -q "Test bio"; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
    exit 1
fi

# Test 8: Access users list
echo -n "Test 8: Testing users list... "
USERS_RESPONSE=$(curl -s -b /tmp/cookies.txt "$BASE_URL/users")
if echo "$USERS_RESPONSE" | grep -q "Registered Users"; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
    exit 1
fi

# Test 9: Access report page
echo -n "Test 9: Testing report page... "
REPORT_RESPONSE=$(curl -s -b /tmp/cookies.txt "$BASE_URL/report")
if echo "$REPORT_RESPONSE" | grep -q "Report URL"; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
    exit 1
fi

# Test 10: Check admin user exists (without logging in)
echo -n "Test 10: Verifying admin user setup... "
# Try to login with wrong password (should fail but user should exist)
ADMIN_CHECK=$(curl -s -X POST "$BASE_URL/login" \
    -d "username=admin&password=wrongpassword")

if echo "$ADMIN_CHECK" | grep -q "Invalid credentials"; then
    echo -e "${GREEN}✓ PASS${NC} (Admin user exists)"
else
    echo -e "${YELLOW}⚠ WARNING${NC} (Cannot verify admin user)"
fi

# Test 11: Check CSRF vulnerability (no token required)
echo -n "Test 11: Verifying CSRF vulnerability... "
PROFILE_HTML=$(curl -s -b /tmp/cookies.txt "$BASE_URL/profile")
if echo "$PROFILE_HTML" | grep -q 'name="_csrf_token"' || echo "$PROFILE_HTML" | grep -q 'csrf_token'; then
    echo -e "${RED}✗ FAIL${NC} (CSRF protection detected - vulnerability not present!)"
    exit 1
else
    echo -e "${GREEN}✓ PASS${NC} (No CSRF protection - vulnerable as intended)"
fi

# Cleanup
rm -f /tmp/cookies.txt /tmp/register_response.html /tmp/login_response.html /tmp/update_response.html

echo ""
echo "=========================================="
echo -e "${GREEN}All tests passed! ✓${NC}"
echo "=========================================="
echo ""
echo "Service is ready for CTF challenge!"
echo "Access at: $BASE_URL"
echo ""
echo "Challenge Information:"
echo "  - Flag format: centralctf{...}"
echo "  - Vulnerability: CSRF on /update_profile"
echo "  - Admin bot: Reports feature"
echo ""
echo "For students: Open $BASE_URL and start hacking!"
echo "For instructors: See SOLUTION.md for the solution"
echo ""
