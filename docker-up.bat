@echo off
echo 🔄 Syncing environment variables from backend/.env...
if not exist "backend\.env" (
    echo ❌ backend\.env file not found!
    echo Please create backend\.env file first using the template:
    echo copy backend\env.template backend\.env
    pause
    exit /b 1
)

copy "backend\.env" ".env" >nul 2>&1
if errorlevel 1 (
    echo ❌ Failed to copy .env file!
    pause
    exit /b 1
)
echo ✅ Successfully copied backend\.env to current directory

echo 🚀 Starting Docker Compose...
docker-compose up -d
if errorlevel 1 (
    echo ❌ Docker Compose failed!
    pause
    exit /b 1
)

echo 🎉 All done! Your containers should be running now.
echo Check with: docker ps
pause
