#!/bin/bash

# SmartHQ Add-on Build Script
set -e

# Check for config.yaml
if [ ! -f config.yaml ]; then
    echo "Error: config.yaml not found. Please run this script from the add-on directory."
    exit 1
fi

# Create build directory
BUILD_DIR="build"
echo "Cleaning and creating build directory..."
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# Copy files to build directory
echo "Copying files to build directory..."
cp -r *.py *.yaml *.txt *.md Dockerfile "$BUILD_DIR/" 2>/dev/null || true
cp -r docs "$BUILD_DIR/" 2>/dev/null || true

# Create .env.template
cat > "$BUILD_DIR/.env.template" << EOF
# SmartHQ Add-on Environment Variables
# Copy this to .env and fill in your values
USERNAME=your_smarthq_username
PASSWORD=your_smarthq_password
REGION=US
WEBSOCKET_URL=wss://ws-us-west-2.mysmarthq.com
ENABLE_ALERTS=true
ENABLE_SERVICES=true
ENABLE_PRESENCE=true
ENABLE_COMMANDS=true
LOG_LEVEL=INFO
RECONNECT_INTERVAL=30
HEARTBEAT_INTERVAL=60
HOST=0.0.0.0
PORT=8080
EOF

# Create run.sh
cat > "$BUILD_DIR/run.sh" << 'EOF'
#!/bin/bash
# SmartHQ Add-on Run Script
set -e
if [ ! -f .env ]; then
    echo "Warning: .env file not found. Using default settings."
    echo "Copy .env.template to .env and configure your settings."
fi
if [ ! -d venv ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate
echo "Installing dependencies..."
pip install -r requirements.txt
echo "Starting application..."
python main.py
EOF
chmod +x "$BUILD_DIR/run.sh"

# Create build-docker.sh
cat > "$BUILD_DIR/build-docker.sh" << 'EOF'
#!/bin/bash
# Build Docker image for SmartHQ Add-on
set -e
IMAGE_NAME=smarthq-appliance-control
TAG=latest
echo "Building Docker image: $IMAGE_NAME:$TAG"
docker build -t $IMAGE_NAME:$TAG .
echo "Docker image built successfully!"
echo "To run: docker run -p 8080:8080 --env-file .env $IMAGE_NAME:$TAG"
EOF
chmod +x "$BUILD_DIR/build-docker.sh"

# Create install-addon.sh
cat > "$BUILD_DIR/install-addon.sh" << 'EOF'
#!/bin/bash
# Install SmartHQ Add-on in Home Assistant
set -e
ADDON_DIR="/config/addons/local/smarthq_appliance_control"
echo "Installing SmartHQ Add-on to Home Assistant..."
sudo mkdir -p "$ADDON_DIR"
sudo cp -r * "$ADDON_DIR/"
sudo chown -R homeassistant:homeassistant "$ADDON_DIR"
sudo chmod -R 755 "$ADDON_DIR"
echo "Add-on installed successfully!"
echo "You can now install it from the Home Assistant Add-ons page."
echo "Look for SmartHQ Appliance Control in the Local Add-ons section."
EOF
chmod +x "$BUILD_DIR/install-addon.sh"

echo "Build completed successfully!"
echo "Build directory: $BUILD_DIR"
echo ""
echo "Next steps:"
echo "1. cd $BUILD_DIR"
echo "2. Copy .env.template to .env and configure your settings"
echo "3. ./run.sh to start the add-on locally"
echo "4. Or run ./build-docker.sh to build a Docker image"
echo "5. Or run ./install-addon.sh to install in Home Assistant" 