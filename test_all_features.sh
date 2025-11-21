#!/bin/bash

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     DASHBOARD FEATURES COMPREHENSIVE TEST                  ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

BASE_URL="http://localhost:5003"
PASS=0
FAIL=0

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test function
test_endpoint() {
    local name=$1
    local method=$2
    local endpoint=$3
    local data=$4
    
    echo -n "Testing $name... "
    
    if [ "$method" = "POST" ]; then
        response=$(curl -s -X POST "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data" \
            -w "\n%{http_code}")
    else
        response=$(curl -s "$BASE_URL$endpoint" -w "\n%{http_code}")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" = "200" ]; then
        success=$(echo "$body" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('success', False))" 2>/dev/null)
        if [ "$success" = "True" ]; then
            echo -e "${GREEN}✓ PASS${NC}"
            ((PASS++))
            return 0
        fi
    fi
    
    echo -e "${RED}✗ FAIL${NC} (HTTP $http_code)"
    ((FAIL++))
    return 1
}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  EMAIL VALIDATOR"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

test_endpoint "Email Validation" "POST" "/api/validate" '{
    "emails": ["test@gmail.com", "invalid@test.com"],
    "options": {
        "check_mx": true,
        "check_smtp": false,
        "max_workers": 5,
        "use_cache": false
    }
}'

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  EMAIL GENERATOR"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

test_endpoint "Random Email Generation" "POST" "/api/generate" '{
    "email_type": "random",
    "text": "test",
    "total": 10,
    "domains": ["gmail.com", "yahoo.com"],
    "char_type": "lowercase",
    "number_type": "suffix"
}'

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  EMAIL EXTRACTOR"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

test_endpoint "Email Extraction" "POST" "/api/extract" '{
    "text": "Contact us at support@example.com or admin@test.com for help",
    "options": {
        "remove_dups": true
    }
}'

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  EMAIL FORMATTER"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

test_endpoint "Email Formatting" "POST" "/api/format" '{
    "emails": ["Test@Gmail.com", "ADMIN@Yahoo.com"],
    "case_format": "lowercase",
    "sort_type": "alphabetical"
}'

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5️⃣  EMAIL FILTER"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

test_endpoint "Email Filtering" "POST" "/api/filter" '{
    "emails": ["test@gmail.com", "admin@yahoo.com", "user@outlook.com"],
    "filters": {
        "domains": ["gmail.com", "yahoo.com"]
    }
}'

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6️⃣  EMAIL ANALYZER"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

test_endpoint "Email Analysis" "POST" "/api/analyze" '{
    "emails": ["user1@gmail.com", "user2@yahoo.com", "admin@gmail.com"]
}'

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "7️⃣  EMAIL DEDUPLICATOR"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

test_endpoint "Email Deduplication" "POST" "/api/deduplicate" '{
    "emails": ["test@gmail.com", "TEST@gmail.com", "test@gmail.com"],
    "method": "case_insensitive",
    "keep_strategy": "first"
}'

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "8️⃣  EMAIL SPLITTER"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

test_endpoint "Email Splitting" "POST" "/api/split" '{
    "emails": ["email1@test.com", "email2@test.com", "email3@test.com"],
    "method": "count",
    "count": 2
}'

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "9️⃣  EMAIL COMBINER"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

test_endpoint "Email Combining" "POST" "/api/combine" '{
    "email_lists": [
        ["email1@test.com", "email2@test.com"],
        ["email2@test.com", "email3@test.com"]
    ],
    "method": "unique"
}'

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔟 BATCH PROCESSOR"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

test_endpoint "Batch Processing" "POST" "/api/batch" '{
    "emails": ["test1@gmail.com", "test2@yahoo.com"],
    "batch_size": 100,
    "operation": "deduplicate",
    "max_workers": 5
}'

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣1️⃣ DATABASE STATS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

test_endpoint "Database Statistics" "GET" "/api/db/stats" ""

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣2️⃣ HEALTH CHECK"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

test_endpoint "Health Check" "GET" "/api/health" ""

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    TEST SUMMARY                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo -e "✅ PASSED: ${GREEN}$PASS${NC}"
echo -e "❌ FAILED: ${RED}$FAIL${NC}"
echo -e "📊 TOTAL:  $(($PASS + $FAIL))"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED! Dashboard features are working perfectly!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some tests failed. Check the logs above.${NC}"
    exit 1
fi
