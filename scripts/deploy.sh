#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Starting deployment process..."

# Navigate to the project root directory (assuming script is run from scripts/ or root)
# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "Project root: $PROJECT_ROOT"

# Check if git is available and pull latest changes
if command -v git &> /dev/null; then
    echo "Pulling latest changes from git..."
    git pull
else
    echo "Git not found or not a git repository. Skipping git pull."
fi

# Build and start containers using docker-compose
echo "Building and starting containers..."
if [ -f "docker/docker-compose.yml" ]; then
    docker-compose -f docker/docker-compose.yml up -d --build
else
    echo "Error: docker/docker-compose.yml not found!"
    exit 1
fi

echo "Deployment completed successfully!"
echo "Backend is running at http://localhost:8000"
