#!/usr/bin/env python3
"""
Cloudflare DNS Setup Script
Connect mochiphoto.click to VPS 14.225.210.195
"""

import requests
import json
import sys

# Configuration
DOMAIN = "mochiphoto.click"
VPS_IP = "14.225.210.195"
CF_EMAIL = "Biagency97@gmail.com"

def setup_dns(api_key):
    """Setup DNS records using Cloudflare API"""
    
    print("=" * 50)
    print("  Cloudflare DNS Configuration")
    print("=" * 50)
    print(f"\nDomain: {DOMAIN}")
    print(f"Target IP: {VPS_IP}")
    print(f"Email: {CF_EMAIL}\n")
    
    headers = {
        "X-Auth-Email": CF_EMAIL,
        "X-Auth-Key": api_key,
        "Content-Type": "application/json"
    }
    
    # Step 1: Get Zone ID
    print("Step 1: Getting Zone ID...")
    print("-" * 40)
    
    response = requests.get(
        f"https://api.cloudflare.com/client/v4/zones?name={DOMAIN}",
        headers=headers
    )
    
    if not response.ok:
        print(f"❌ HTTP Error: {response.status_code}")
        print(response.text)
        return False
    
    data = response.json()
    
    if not data.get('success'):
        print("❌ API Error:")
        print(json.dumps(data.get('errors', []), indent=2))
        return False
    
    if not data.get('result'):
        print(f"❌ Domain {DOMAIN} not found in your Cloudflare account")
        return False
    
    zone_id = data['result'][0]['id']
    print(f"✅ Zone ID: {zone_id}\n")
    
    # Step 2: Check existing records
    print("Step 2: Checking existing DNS records...")
    print("-" * 40)
    
    response = requests.get(
        f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?type=A",
        headers=headers
    )
    
    if response.ok:
        existing = response.json().get('result', [])
        if existing:
            print("Current A records:")
            for record in existing:
                print(f"  - {record['name']} → {record['content']}")
        else:
            print("  No existing A records")
    print()
    
    # Step 3: Create/Update DNS records
    print("Step 3: Creating/Updating DNS records...")
    print("-" * 40)
    
    def setup_record(name, content, proxied=True):
        full_name = f"{name}.{DOMAIN}" if name != "@" else DOMAIN
        print(f"\nSetting up: {full_name} → {content}")
        
        # Check if exists
        response = requests.get(
            f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?type=A&name={full_name}",
            headers=headers
        )
        
        existing_records = response.json().get('result', [])
        
        record_data = {
            "type": "A",
            "name": name,
            "content": content,
            "ttl": 1,
            "proxied": proxied
        }
        
        if existing_records:
            # Update existing
            record_id = existing_records[0]['id']
            print(f"  → Updating existing record (ID: {record_id})...")
            
            response = requests.put(
                f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}",
                headers=headers,
                json=record_data
            )
        else:
            # Create new
            print("  → Creating new record...")
            
            response = requests.post(
                f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records",
                headers=headers,
                json=record_data
            )
        
        result = response.json()
        
        if result.get('success'):
            print("  ✅ Success!")
            return True
        else:
            print("  ❌ Failed!")
            print(f"  Errors: {result.get('errors')}")
            return False
    
    # Setup root and www
    success_root = setup_record("@", VPS_IP)
    success_www = setup_record("www", VPS_IP)
    
    print("\n" + "=" * 50)
    if success_root and success_www:
        print("  ✅ DNS Configuration Complete!")
    else:
        print("  ⚠️  DNS Configuration Partially Complete")
    print("=" * 50)
    
    print(f"\nDNS Records:")
    print(f"  • {DOMAIN}           → {VPS_IP}")
    print(f"  • www.{DOMAIN}       → {VPS_IP}")
    print(f"\nCloudflare Proxy: ✅ Enabled (SSL + CDN)")
    print(f"\nNext Steps:")
    print(f"  1. Wait 1-5 minutes for DNS propagation")
    print(f"  2. Update Nginx to accept domain: {DOMAIN}")
    print(f"  3. Enable SSL on Cloudflare (if not already)")
    print(f"\nCheck DNS:")
    print(f"  • https://dnschecker.org/#A/{DOMAIN}")
    print(f"  • dig {DOMAIN}")
    print()
    
    return True

if __name__ == "__main__":
    print("\n🔑 Cloudflare API Key Required\n")
    print("To get your Global API Key:")
    print("1. Login: https://dash.cloudflare.com/login")
    print(f"   Email: {CF_EMAIL}")
    print("   Password: (one of: Bg19051997@#, Bg190597@, bighi1997)")
    print()
    print("2. Go to: https://dash.cloudflare.com/profile/api-tokens")
    print("3. Scroll to 'API Keys' section")
    print("4. Click 'View' next to 'Global API Key'")
    print("5. Enter password and copy the key")
    print()
    
    api_key = input("Paste your Cloudflare Global API Key: ").strip()
    
    if not api_key:
        print("❌ No API key provided")
        sys.exit(1)
    
    # Save API key for future use
    with open(".cloudflare_api_key", "w") as f:
        f.write(api_key)
    
    print()
    success = setup_dns(api_key)
    
    sys.exit(0 if success else 1)
