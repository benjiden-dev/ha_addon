#!/bin/bash
# Build Docker image for SmartHQ Add-on
set -e
IMAGE_NAME=smarthq-appliance-control
TAG=latest
echo "Building Docker image: $IMAGE_NAME:$TAG"
docker build -t $IMAGE_NAME:$TAG .
echo "Docker image built successfully!"
echo "To run: docker run -p 8080:8080 --env-file .env $IMAGE_NAME:$TAG"
