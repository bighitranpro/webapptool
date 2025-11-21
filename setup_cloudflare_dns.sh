#!/bin/bash

# Cloudflare DNS Setup Script
# Connect domain mochiphoto.click to VPS 14.225.210.195

set -e

echo "=========================================="
echo "  Cloudflare DNS Configuration"
echo "=========================================="
echo ""

DOMAIN="mochiphoto.click"
VPS_IP="14.225.210.195"
CF_EMAIL="Biagency97@gmail.com"

# We need Cloudflare API Token
echo "Step 1: Get Cloudflare API Token"
echo "--------------------------------------"
echo "Please follow these steps to get your API token:"
echo ""
echo "1. Go to: https://dash.cloudflare.com/profile/api-tokens"
echo "2. Click 'Create Token'"
echo "3. Use template: 'Edit zone DNS'"
echo "4. Set Zone Resources: Include -> Specific zone -> mochiphoto.click"
echo "5. Click 'Continue to summary' then 'Create Token'"
echo "6. Copy the token (starts with: ey...)"
echo ""
echo "Alternatively, use Global API Key:"
echo "1. Go to: https://dash.cloudflare.com/profile/api-tokens"
echo "2. Scroll down to 'API Keys'"
echo "3. Click 'View' on 'Global API Key'"
echo "4. Copy the key"
echo ""

# Check if we have cloudflare credentials
if [ -f ~/.cloudflare_token ]; then
    echo "✅ Found existing Cloudflare credentials"
    CF_TOKEN=$(cat ~/.cloudflare_token)
else
    echo "⚠️  No Cloudflare credentials found"
    echo ""
    read -p "Enter your Cloudflare API Token or Global API Key: " CF_TOKEN
    echo "$CF_TOKEN" > ~/.cloudflare_token
    chmod 600 ~/.cloudflare_token
fi

echo ""
echo "Step 2: Get Zone ID for $DOMAIN"
echo "--------------------------------------"

# Get Zone ID
ZONE_RESPONSE=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones?name=$DOMAIN" \
  -H "Authorization: Bearer $CF_TOKEN" \
  -H "Content-Type: application/json")

ZONE_ID=$(echo $ZONE_RESPONSE | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)

if [ -z "$ZONE_ID" ]; then
    echo "❌ Failed to get Zone ID. Trying with Global API Key method..."
    
    # Try with Global API Key method
    read -p "Enter your Cloudflare Global API Key: " CF_GLOBAL_KEY
    
    ZONE_RESPONSE=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones?name=$DOMAIN" \
      -H "X-Auth-Email: $CF_EMAIL" \
      -H "X-Auth-Key: $CF_GLOBAL_KEY" \
      -H "Content-Type: application/json")
    
    ZONE_ID=$(echo $ZONE_RESPONSE | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)
    
    if [ -z "$ZONE_ID" ]; then
        echo "❌ Still failed. Please check your credentials."
        echo "Response: $ZONE_RESPONSE"
        exit 1
    fi
    
    # Save global key for later use
    echo "$CF_GLOBAL_KEY" > ~/.cloudflare_global_key
    chmod 600 ~/.cloudflare_global_key
    USE_GLOBAL_KEY=1
fi

echo "✅ Zone ID: $ZONE_ID"
echo ""

echo "Step 3: Check existing DNS records"
echo "--------------------------------------"

if [ "$USE_GLOBAL_KEY" = "1" ]; then
    CF_GLOBAL_KEY=$(cat ~/.cloudflare_global_key)
    DNS_RECORDS=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records?type=A" \
      -H "X-Auth-Email: $CF_EMAIL" \
      -H "X-Auth-Key: $CF_GLOBAL_KEY" \
      -H "Content-Type: application/json")
else
    DNS_RECORDS=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records?type=A" \
      -H "Authorization: Bearer $CF_TOKEN" \
      -H "Content-Type: application/json")
fi

echo "Current A records:"
echo "$DNS_RECORDS" | grep -o '"name":"[^"]*' | cut -d'"' -f4 || echo "No A records found"
echo ""

echo "Step 4: Create/Update DNS Records"
echo "--------------------------------------"

# Function to create or update DNS record
create_or_update_record() {
    local NAME=$1
    local TYPE=$2
    local CONTENT=$3
    local PROXIED=$4
    
    echo "Processing: $NAME.$DOMAIN ($TYPE -> $CONTENT)"
    
    # Check if record exists
    if [ "$USE_GLOBAL_KEY" = "1" ]; then
        RECORD_ID=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records?type=$TYPE&name=$NAME.$DOMAIN" \
          -H "X-Auth-Email: $CF_EMAIL" \
          -H "X-Auth-Key: $CF_GLOBAL_KEY" \
          -H "Content-Type: application/json" | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)
    else
        RECORD_ID=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records?type=$TYPE&name=$NAME.$DOMAIN" \
          -H "Authorization: Bearer $CF_TOKEN" \
          -H "Content-Type: application/json" | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)
    fi
    
    if [ -z "$RECORD_ID" ]; then
        # Create new record
        echo "  → Creating new record..."
        if [ "$USE_GLOBAL_KEY" = "1" ]; then
            RESPONSE=$(curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records" \
              -H "X-Auth-Email: $CF_EMAIL" \
              -H "X-Auth-Key: $CF_GLOBAL_KEY" \
              -H "Content-Type: application/json" \
              --data "{\"type\":\"$TYPE\",\"name\":\"$NAME\",\"content\":\"$CONTENT\",\"ttl\":1,\"proxied\":$PROXIED}")
        else
            RESPONSE=$(curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records" \
              -H "Authorization: Bearer $CF_TOKEN" \
              -H "Content-Type: application/json" \
              --data "{\"type\":\"$TYPE\",\"name\":\"$NAME\",\"content\":\"$CONTENT\",\"ttl\":1,\"proxied\":$PROXIED}")
        fi
    else
        # Update existing record
        echo "  → Updating existing record (ID: $RECORD_ID)..."
        if [ "$USE_GLOBAL_KEY" = "1" ]; then
            RESPONSE=$(curl -s -X PUT "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records/$RECORD_ID" \
              -H "X-Auth-Email: $CF_EMAIL" \
              -H "X-Auth-Key: $CF_GLOBAL_KEY" \
              -H "Content-Type: application/json" \
              --data "{\"type\":\"$TYPE\",\"name\":\"$NAME\",\"content\":\"$CONTENT\",\"ttl\":1,\"proxied\":$PROXIED}")
        else
            RESPONSE=$(curl -s -X PUT "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records/$RECORD_ID" \
              -H "Authorization: Bearer $CF_TOKEN" \
              -H "Content-Type: application/json" \
              --data "{\"type\":\"$TYPE\",\"name\":\"$NAME\",\"content\":\"$CONTENT\",\"ttl\":1,\"proxied\":$PROXIED}")
        fi
    fi
    
    SUCCESS=$(echo $RESPONSE | grep -o '"success":[^,]*' | cut -d':' -f2)
    if [ "$SUCCESS" = "true" ]; then
        echo "  ✅ Success"
    else
        echo "  ❌ Failed: $RESPONSE"
    fi
    echo ""
}

# Create DNS records
echo "Creating DNS records for $DOMAIN pointing to $VPS_IP"
echo ""

# Root domain (@ or mochiphoto.click)
create_or_update_record "mochiphoto.click" "A" "$VPS_IP" "true"

# www subdomain
create_or_update_record "www" "A" "$VPS_IP" "true"

echo ""
echo "=========================================="
echo "  ✅ DNS Configuration Complete!"
echo "=========================================="
echo ""
echo "DNS Records Created:"
echo "  • mochiphoto.click         → $VPS_IP (Proxied via Cloudflare)"
echo "  • www.mochiphoto.click     → $VPS_IP (Proxied via Cloudflare)"
echo ""
echo "Next Steps:"
echo "  1. Wait 1-5 minutes for DNS propagation"
echo "  2. Update Nginx configuration to accept domain names"
echo "  3. Setup SSL certificate (Cloudflare provides free SSL)"
echo ""
echo "You can check DNS propagation:"
echo "  • https://dnschecker.org/#A/mochiphoto.click"
echo "  • dig mochiphoto.click"
echo "  • nslookup mochiphoto.click"
echo ""

