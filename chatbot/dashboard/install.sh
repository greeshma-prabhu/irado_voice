#!/bin/bash
# Irado Chatbot Dashboard Installation Script

echo "🚀 Installing Irado Chatbot Dashboard..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root (use sudo)"
    exit 1
fi

# Create virtual environment and install dependencies
echo "📦 Creating virtual environment and installing dependencies..."
cd /opt/irado/chatbot/dashboard
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Copy systemd service file
echo "🔧 Installing systemd service..."
cp irado-dashboard.service /etc/systemd/system/

# Reload systemd
systemctl daemon-reload

# Enable service
systemctl enable irado-dashboard.service

# Start service
echo "🚀 Starting Irado Chatbot Dashboard..."
systemctl start irado-dashboard.service

# Check status
echo "📊 Checking service status..."
systemctl status irado-dashboard.service --no-pager

echo ""
echo "✅ Installation complete!"
echo "🌐 Dashboard available at: http://localhost:3255"
echo ""
echo "📋 Service management commands:"
echo "  sudo systemctl start irado-dashboard    # Start service"
echo "  sudo systemctl stop irado-dashboard     # Stop service"
echo "  sudo systemctl restart irado-dashboard  # Restart service"
echo "  sudo systemctl status irado-dashboard   # Check status"
echo "  sudo systemctl logs irado-dashboard     # View logs"
echo ""
