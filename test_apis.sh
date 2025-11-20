#!/bin/bash

echo "=== Testing Email Tool Pro APIs ==="
echo ""

echo "1. Testing /api/health"
curl -s http://localhost:5000/api/health | python3 -m json.tool | head -20
echo ""

echo "2. Testing /api/generate (Generate 3 emails)"
curl -s -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"email_type":"random","text":"user","total":3,"domain":"gmail.com","char_type":"lowercase","number_type":"suffix"}' \
  | python3 -m json.tool
echo ""

echo "3. Testing /api/extract (Extract emails from text)"
curl -s -X POST http://localhost:5000/api/extract \
  -H "Content-Type: application/json" \
  -d '{"text":"Contact us at support@example.com or sales@test.com","options":{"remove_dups":true}}' \
  | python3 -m json.tool
echo ""

echo "4. Testing /api/format (Format emails)"
curl -s -X POST http://localhost:5000/api/format \
  -H "Content-Type: application/json" \
  -d '{"emails":["TEST@GMAIL.COM","user@yahoo.com"],"case_format":"lowercase","sort_type":"alphabetical"}' \
  | python3 -m json.tool
echo ""

echo "5. Testing /api/deduplicate (Remove duplicates)"
curl -s -X POST http://localhost:5000/api/deduplicate \
  -H "Content-Type: application/json" \
  -d '{"emails":["test@gmail.com","TEST@gmail.com","user@yahoo.com"],"method":"case_insensitive"}' \
  | python3 -m json.tool
echo ""

echo "=== All tests completed ==="
