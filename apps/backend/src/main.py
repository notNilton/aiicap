"""
AIICAP Backend API

FastAPI backend for image generation and correction services.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from .routers import images, generation, correction


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown events"""
    # Initialize database on startup
    from packages.shared.database import init_db
    init_db()
    print("[OK] Database initialized")
    yield
    # Cleanup on shutdown
    print("[OK] Shutting down")


app = FastAPI(
    title="AIICAP API",
    description="API for AI Image Correction and Processing",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for serving images
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./data/uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Include routers
app.include_router(images.router, prefix="/api/images", tags=["images"])
app.include_router(generation.router, prefix="/api/generate", tags=["generation"])
app.include_router(correction.router, prefix="/api/correct", tags=["correction"])


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "aiicap-backend"}


@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "name": "AIICAP API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }
