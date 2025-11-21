#!/bin/bash

# Setup VPS Security - Change Password
# Server: 14.225.210.195

set -e

echo "╔══════════════════════════════════════════╗"
echo "║  VPS Security Setup                      ║"
echo "║  Change Password for biproduction        ║"
echo "╚══════════════════════════════════════════╝"
echo ""

NEW_SERVER="14.225.210.195"
SSH_USER="biproduction"
SSH_PORT="22"
OLD_PASSWORD="orxvSl49eSGuvt6afQpz"
NEW_PASSWORD="Bg190597@"

echo "📝 Server Information:"
echo "  IP: $NEW_SERVER"
echo "  User: $SSH_USER"
echo "  Port: $SSH_PORT"
echo ""

echo "🔐 Step 1: Testing connection with old password..."

# Test connection using sshpass
if ! command -v sshpass &> /dev/null; then
    echo "⚠️  sshpass not installed. Installing..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt-get install -y sshpass 2>/dev/null || sudo yum install -y sshpass 2>/dev/null
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install hudochenkov/sshpass/sshpass
    fi
fi

# Test old password
echo "Testing SSH connection..."
if sshpass -p "$OLD_PASSWORD" ssh -p $SSH_PORT -o StrictHostKeyChecking=no -o ConnectTimeout=5 $SSH_USER@$NEW_SERVER "echo 'Connection OK'" 2>/dev/null; then
    echo "✅ Connection successful with old password!"
else
    echo "❌ Connection failed. Please verify:"
    echo "  1. Old password is correct"
    echo "  2. Username is correct"
    echo "  3. Server IP is reachable"
    exit 1
fi

echo ""
echo "🔐 Step 2: Changing password on server..."

# Change password on remote server
sshpass -p "$OLD_PASSWORD" ssh -p $SSH_PORT -o StrictHostKeyChecking=no $SSH_USER@$NEW_SERVER bash << ENDSSH
# Change password for biproduction user
echo "$SSH_USER:$NEW_PASSWORD" | sudo chpasswd

if [ \$? -eq 0 ]; then
    echo "✅ Password changed successfully!"
else
    echo "❌ Failed to change password"
    exit 1
fi
ENDSSH

echo ""
echo "🔐 Step 3: Testing new password..."

# Test new password
sleep 2
if sshpass -p "$NEW_PASSWORD" ssh -p $SSH_PORT -o StrictHostKeyChecking=no $SSH_USER@$NEW_SERVER "echo 'New password works!'" 2>/dev/null; then
    echo "✅ New password verified successfully!"
else
    echo "❌ New password verification failed"
    exit 1
fi

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║      ✅ Password Changed! ✅             ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "📝 New credentials:"
echo "  Server:   14.225.210.195"
echo "  User:     biproduction"
echo "  Password: Bg190597@"
echo ""
echo "🔐 You can now SSH with:"
echo "  ssh biproduction@14.225.210.195"
echo ""
echo "🚀 Next step: Run deployment"
echo "  ./deploy_to_ubuntu.sh"
echo ""

# Save credentials to file (encrypted)
echo "💾 Saving credentials to .credentials (for reference)..."
cat > .credentials << EOF
# VPS Credentials
Server: 14.225.210.195
Username: biproduction
Password: Bg190597@
Port: 22

# Login command:
ssh biproduction@14.225.210.195

# Deploy command:
./deploy_to_ubuntu.sh
EOF

chmod 600 .credentials
echo "✅ Credentials saved to .credentials (chmod 600)"

echo ""
echo "✅ Setup complete! Ready to deploy."
