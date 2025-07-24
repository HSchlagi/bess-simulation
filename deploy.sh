#!/bin/bash

# BESS Simulation - Automated Deployment Script
# Usage: ./deploy.sh [production|staging]

set -e  # Exit on any error

ENVIRONMENT=${1:-production}
PROJECT_DIR="/var/www/bess-simulation"
BACKUP_DIR="/var/backups/bess-simulation"

echo "🚀 Starting BESS Simulation deployment for $ENVIRONMENT..."

# Create backup before deployment
echo "📦 Creating backup..."
mkdir -p $BACKUP_DIR
DATE=$(date +%Y%m%d_%H%M%S)
if [ -f "$PROJECT_DIR/instance/bess.db" ]; then
    cp "$PROJECT_DIR/instance/bess.db" "$BACKUP_DIR/bess_$DATE.db"
    echo "✅ Database backed up to $BACKUP_DIR/bess_$DATE.db"
fi

# Navigate to project directory
cd $PROJECT_DIR

# Pull latest changes
echo "📥 Pulling latest changes from Git..."
git fetch origin
git reset --hard origin/main

# Activate virtual environment
echo "🐍 Activating Python virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📦 Installing/updating Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Set proper permissions
echo "🔐 Setting proper permissions..."
chown -R www-data:www-data $PROJECT_DIR
chmod -R 755 $PROJECT_DIR
chmod 664 $PROJECT_DIR/instance/bess.db 2>/dev/null || true

# Restart services
echo "🔄 Restarting services..."
systemctl restart bess-simulation
systemctl reload nginx

# Check service status
echo "🔍 Checking service status..."
if systemctl is-active --quiet bess-simulation; then
    echo "✅ BESS Simulation service is running"
else
    echo "❌ BESS Simulation service failed to start"
    journalctl -u bess-simulation --no-pager -n 20
    exit 1
fi

if systemctl is-active --quiet nginx; then
    echo "✅ Nginx service is running"
else
    echo "❌ Nginx service failed to start"
    exit 1
fi

# Test application
echo "🧪 Testing application..."
sleep 5  # Wait for services to fully start
if curl -f http://localhost > /dev/null 2>&1; then
    echo "✅ Application is responding"
else
    echo "❌ Application is not responding"
    exit 1
fi

echo "🎉 Deployment completed successfully!"
echo "📊 Application is now running at: http://$(hostname -I | awk '{print $1}')"
echo "📋 Recent logs: journalctl -u bess-simulation -f" 