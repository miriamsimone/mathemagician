"""Main FastAPI application"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.models.responses import HealthResponse
from app import __version__

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info(f"Starting Mathemagician API v{__version__}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Redis: {settings.redis_host}:{settings.redis_port}")
    logger.info(f"GCS Bucket: {settings.gcs_bucket}")

    # Start background worker
    from app.workers.render_worker import render_worker
    render_worker.start()

    yield

    logger.info("Shutting down Mathemagician API")
    render_worker.stop()


# Create FastAPI app
app = FastAPI(
    title="Mathemagician API",
    description="Math visualization API powered by Manim",
    version=__version__,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version=__version__,
        environment=settings.environment
    )


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "name": "Mathemagician API",
        "version": __version__,
        "docs": "/docs",
        "health": "/health"
    }


# Import and include routers
from app.api import generate, status
app.include_router(generate.router, tags=["Generate"])
app.include_router(status.router, tags=["Status"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
