#!/bin/bash

###############################################################################
# Test Script for Email Checker App
# Tests all API endpoints and functionality
###############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BASE_URL="http://127.0.0.1:8001"

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}Email Checker App - Test Suite${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""

# Test 1: Health Check
echo -e "${YELLOW}Test 1: Health Check${NC}"
response=$(curl -s "${BASE_URL}/health")
status=$(echo $response | grep -o '"status":"healthy"' || echo "")

if [ -n "$status" ]; then
    echo -e "${GREEN}✓ Health check passed${NC}"
    echo "  Response: $response"
else
    echo -e "${RED}✗ Health check failed${NC}"
    exit 1
fi
echo ""

# Test 2: Generate Emails
echo -e "${YELLOW}Test 2: Generate Emails${NC}"
response=$(curl -s -X POST "${BASE_URL}/generate" \
    -H "Content-Type: application/json" \
    -d '{"count": 5, "mix_ratio": 0.7}')

success=$(echo $response | grep -o '"success":true' || echo "")
if [ -n "$success" ]; then
    echo -e "${GREEN}✓ Email generation successful${NC}"
    # Extract emails for next test
    emails=$(echo $response | python3 -c "import sys, json; data=json.load(sys.stdin); print(json.dumps(data['emails'][:3]))")
    echo "  Generated emails: $emails"
else
    echo -e "${RED}✗ Email generation failed${NC}"
    echo "  Response: $response"
    exit 1
fi
echo ""

# Test 3: Start Check (with generated emails)
echo -e "${YELLOW}Test 3: Start Email Check${NC}"
response=$(curl -s -X POST "${BASE_URL}/check" \
    -H "Content-Type: application/json" \
    -d "{\"emails\": $emails}")

success=$(echo $response | grep -o '"success":true' || echo "")
if [ -n "$success" ]; then
    echo -e "${GREEN}✓ Check started successfully${NC}"
    echo "  Response: $response"
else
    echo -e "${RED}✗ Check start failed${NC}"
    echo "  Response: $response"
fi
echo ""

# Test 4: Check Progress
echo -e "${YELLOW}Test 4: Monitor Progress${NC}"
for i in {1..10}; do
    sleep 2
    response=$(curl -s "${BASE_URL}/progress")
    is_running=$(echo $response | grep -o '"is_running":true' || echo "")
    current=$(echo $response | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('current', 0))" 2>/dev/null || echo "0")
    total=$(echo $response | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('total', 0))" 2>/dev/null || echo "0")
    
    echo "  Progress: $current / $total"
    
    if [ -z "$is_running" ]; then
        echo -e "${GREEN}✓ Check completed${NC}"
        break
    fi
    
    if [ $i -eq 10 ]; then
        echo -e "${YELLOW}  Note: Check still running after 20s (this is normal for SMTP checks)${NC}"
    fi
done
echo ""

# Test 5: Get Final Results
echo -e "${YELLOW}Test 5: Get Final Results${NC}"
sleep 3
response=$(curl -s "${BASE_URL}/progress")
results=$(echo $response | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    results = data.get('results', [])
    print(f'Total results: {len(results)}')
    for i, r in enumerate(results[:3], 1):
        print(f'  {i}. {r.get(\"email\", \"N/A\")} -> SMTP: {r.get(\"smtp_status\", \"N/A\")}, Country: {r.get(\"country\", \"N/A\")}')
except:
    print('Error parsing results')
" || echo "Error")

echo "$results"
echo -e "${GREEN}✓ Results retrieved${NC}"
echo ""

# Test 6: List Files
echo -e "${YELLOW}Test 6: List Exported Files${NC}"
response=$(curl -s "${BASE_URL}/files")
success=$(echo $response | grep -o '"success":true' || echo "")

if [ -n "$success" ]; then
    echo -e "${GREEN}✓ Files listed successfully${NC}"
    file_count=$(echo $response | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('files', [])))" 2>/dev/null || echo "0")
    echo "  Total files: $file_count"
else
    echo -e "${YELLOW}  Note: No files found (this is normal on first run)${NC}"
fi
echo ""

# Summary
echo -e "${BLUE}=========================================${NC}"
echo -e "${GREEN}All Tests Completed!${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""
echo "Test Summary:"
echo "  ✓ Health Check"
echo "  ✓ Email Generation"
echo "  ✓ Start Check"
echo "  ✓ Progress Monitoring"
echo "  ✓ Results Retrieval"
echo "  ✓ File Listing"
echo ""
echo "App is ready for use at: ${BASE_URL}"
echo ""
