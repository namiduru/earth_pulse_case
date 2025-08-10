p# Backend API

FastAPI backend for file management with MongoDB and MinIO.

## 📁 Structure

```
backend/
├── app/
│   ├── api/           # API endpoints
│   ├── config/        # Settings & config
│   ├── database/      # DB connection
│   ├── schemas/       # Pydantic models
│   └── services/      # Business logic
├── tests/             # Test files
├── main.py            # Entry point
├── requirements.txt   # Dependencies
└── Dockerfile         # Container config
```

## 🚀 Quick Start

### Docker (Recommended)

```bash
# From project root, run:
docker-up.bat          # Windows
./docker-up.sh         # Unix/Linux/Mac
```

### Manual Development

```bash
# Install
pip install -r requirements.txt

# Run
uvicorn main:app --reload
```

## 🔧 Environment

Copy `env.template` to `.env` and configure:

- MongoDB URL
- MinIO credentials
- API settings
- File upload types

**Note**: For Docker deployment, environment variables are automatically synced from this `.env` file.

## 🧪 Testing

```bash
pytest
```

## 📚 API Docs

- Swagger: `/docs`
- ReDoc: `/redoc`
