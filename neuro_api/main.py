# main.py
from fastapi import FastAPI
from .routers import router as main_router  # Import the main router
from .health import router as health_router
from .config import settings

app = FastAPI(title=settings.app_name, version=settings.version)

# Include Routers
app.include_router(main_router)
app.include_router(health_router)