"""FastAPI application entry point."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import health, metrics
from app.workers.scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    if settings.worker_enabled:
        start_scheduler()
    yield
    # Shutdown
    if settings.worker_enabled:
        stop_scheduler()


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Real-time Amazon Marketing Stream automation system",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(metrics.router, prefix="/api/v1", tags=["metrics"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Amazon Marketing Stream Automation System",
        "version": "0.1.0",
        "status": "operational",
    }

