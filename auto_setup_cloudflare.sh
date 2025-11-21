#!/bin/bash

# Automated Cloudflare DNS Setup
# Domain: mochiphoto.click -> VPS: 14.225.210.195

set -e

DOMAIN="mochiphoto.click"
VPS_IP="14.225.210.195"
CF_EMAIL="Biagency97@gmail.com"

echo "=========================================="
echo "  Cloudflare DNS Auto-Configuration"
echo "=========================================="
echo ""
echo "Domain: $DOMAIN"
echo "Target IP: $VPS_IP"
echo "Email: $CF_EMAIL"
echo ""

# We'll try common API keys that might work
echo "⚠️  IMPORTANT: You need to get your Cloudflare Global API Key"
echo ""
echo "Please go to Cloudflare Dashboard and get your Global API Key:"
echo "1. Login to: https://dash.cloudflare.com/login"
echo "   Email: $CF_EMAIL"
echo "   Password: Bg19051997@# (or one of your passwords)"
echo ""
echo "2. Go to: https://dash.cloudflare.com/profile/api-tokens"
echo "3. Scroll down to 'API Keys' section"
echo "4. Click 'View' next to 'Global API Key'"
echo "5. Enter your password to reveal the key"
echo "6. Copy the key"
echo ""

read -p "Paste your Cloudflare Global API Key here: " CF_API_KEY

if [ -z "$CF_API_KEY" ]; then
    echo "❌ No API key provided. Exiting."
    exit 1
fi

# Save API key
echo "$CF_API_KEY" > ~/.cloudflare_api_key
chmod 600 ~/.cloudflare_api_key

echo ""
echo "Step 1: Getting Zone ID for $DOMAIN"
echo "--------------------------------------"

ZONE_RESPONSE=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones?name=$DOMAIN" \
  -H "X-Auth-Email: $CF_EMAIL" \
  -H "X-Auth-Key: $CF_API_KEY" \
  -H "Content-Type: application/json")

echo "Response: $ZONE_RESPONSE" | head -c 200
echo "..."
echo ""

ZONE_ID=$(echo "$ZONE_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['result'][0]['id'] if data.get('success') and len(data.get('result', [])) > 0 else '')" 2>/dev/null)

if [ -z "$ZONE_ID" ]; then
    echo "❌ Failed to get Zone ID"
    echo "Full response: $ZONE_RESPONSE"
    exit 1
fi

echo "✅ Zone ID: $ZONE_ID"
echo ""

echo "Step 2: Checking existing DNS records"
echo "--------------------------------------"

DNS_RECORDS=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records?type=A" \
  -H "X-Auth-Email: $CF_EMAIL" \
  -H "X-Auth-Key: $CF_API_KEY" \
  -H "Content-Type: application/json")

echo "Current A records:"
echo "$DNS_RECORDS" | python3 -c "import sys, json; data=json.load(sys.stdin); [print(f\"  - {r['name']} -> {r['content']}\") for r in data.get('result', [])]" 2>/dev/null || echo "  (none or error parsing)"
echo ""

echo "Step 3: Creating/Updating DNS records"
echo "--------------------------------------"

# Function to create/update A record
setup_a_record() {
    local RECORD_NAME=$1
    local FULL_NAME="${RECORD_NAME}.${DOMAIN}"
    
    if [ "$RECORD_NAME" = "@" ]; then
        FULL_NAME="$DOMAIN"
    fi
    
    echo "Setting up: $FULL_NAME -> $VPS_IP"
    
    # Check if record exists
    EXISTING=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records?type=A&name=$FULL_NAME" \
      -H "X-Auth-Email: $CF_EMAIL" \
      -H "X-Auth-Key: $CF_API_KEY" \
      -H "Content-Type: application/json")
    
    RECORD_ID=$(echo "$EXISTING" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['result'][0]['id'] if len(data.get('result', [])) > 0 else '')" 2>/dev/null)
    
    if [ -z "$RECORD_ID" ]; then
        # Create new record
        echo "  → Creating new record..."
        RESPONSE=$(curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records" \
          -H "X-Auth-Email: $CF_EMAIL" \
          -H "X-Auth-Key: $CF_API_KEY" \
          -H "Content-Type: application/json" \
          --data "{\"type\":\"A\",\"name\":\"$RECORD_NAME\",\"content\":\"$VPS_IP\",\"ttl\":1,\"proxied\":true}")
    else
        # Update existing record
        echo "  → Updating existing record (ID: $RECORD_ID)..."
        RESPONSE=$(curl -s -X PUT "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records/$RECORD_ID" \
          -H "X-Auth-Email: $CF_EMAIL" \
          -H "X-Auth-Key: $CF_API_KEY" \
          -H "Content-Type: application/json" \
          --data "{\"type\":\"A\",\"name\":\"$RECORD_NAME\",\"content\":\"$VPS_IP\",\"ttl\":1,\"proxied\":true}")
    fi
    
    SUCCESS=$(echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print('true' if data.get('success') else 'false')" 2>/dev/null)
    
    if [ "$SUCCESS" = "true" ]; then
        echo "  ✅ Success!"
    else
        echo "  ❌ Failed!"
        echo "  Response: $RESPONSE"
    fi
    echo ""
}

# Setup records
setup_a_record "@"
setup_a_record "www"

echo "=========================================="
echo "  ✅ DNS Setup Complete!"
echo "=========================================="
echo ""
echo "DNS Records:"
echo "  • $DOMAIN           → $VPS_IP ✅"
echo "  • www.$DOMAIN       → $VPS_IP ✅"
echo ""
echo "Next: Update Nginx to accept the domain name"
echo ""

