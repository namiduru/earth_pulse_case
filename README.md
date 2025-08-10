# Earth Pulse Case

A full-stack application with React frontend and FastAPI backend for file management.

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.8+
- Node.js 16+

### Start Everything

```bash
# 1. Setup environment (required - .env won't be pushed to git)
# Linux/Mac users
cp backend/env.template backend/.env

# Windows users
copy backend\env.template backend\.env

# 2. Start everything
# Windows users (recommended)
docker-up.bat

# Unix/Linux/Mac users
chmod +x docker-up.sh
./docker-up.sh
```

## 📁 Project Structure

```
├── backend/          # FastAPI backend
├── frontend/         # Svelte frontend
├── data/            # MongoDB & MinIO data
└── docker-compose.yml
```

## 🛠️ Development

### Backend

- FastAPI with MongoDB
- File upload/download via MinIO
- RESTful API endpoints

### Frontend

- Svelte with TypeScript
- Tailwind CSS
- File management interface

### Database

- MongoDB for metadata
- MinIO for file storage

## 🧪 Testing

Our comprehensive test suite ensures code quality and reliability:

- **Backend**: 7 test files with 156 test functions covering API endpoints, services, configuration, and database operations
- **Frontend**: 4 test files with 52 test functions covering all UI components and user interactions

All tests are currently passing! 🎯

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 📝 Environment

Copy `backend/env.template` to `backend/.env` and configure:

- MongoDB connection
- MinIO credentials
- API settings

## 🐳 Docker

### Quick Start with Environment Sync

```bash
# Windows users - automatically syncs environment and starts containers
docker-up.bat

# Unix/Linux/Mac users - make executable first, then run
chmod +x docker-up.sh
./docker-up.sh


```

### Manual Docker Compose

```bash
# First, sync environment variables from backend/.env
cp backend/.env .env

# Then build & run
docker-compose up --build

# Stop
docker-compose down
```

**Note**: The automated scripts handle environment synchronization automatically. For manual setup, ensure `backend/.env` exists and contains your configuration.
