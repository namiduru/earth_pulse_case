"""FileDrive API - Main Entry Point"""

import uvicorn
from app.application import app
from app.config.settings import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.application:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    ) 