#!/bin/bash

echo "🔄 Syncing environment variables from backend/.env..."

if [ ! -f "backend/.env" ]; then
    echo "❌ backend/.env file not found!"
    echo "Please create backend/.env file first using the template:"
    echo "cp backend/env.template backend/.env"
    exit 1
fi

cp backend/.env .env
if [ $? -ne 0 ]; then
    echo "❌ Failed to copy .env file!"
    exit 1
fi

echo "✅ Successfully copied backend/.env to current directory"

echo "🚀 Starting Docker Compose..."
docker-compose up -d
if [ $? -ne 0 ]; then
    echo "❌ Docker Compose failed!"
    exit 1
fi

echo "🎉 All done! Your containers should be running now."
echo "Check with: docker ps"
