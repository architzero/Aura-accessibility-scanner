from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import auth, projects, scan
from config import settings
from database import init_db
import os

app = FastAPI(
    title="Aura Accessibility Scanner API",
    version="1.0.0",
    description="AI-powered web accessibility auditing platform"
)

# CORS: Only allow requests from your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure screenshots directory exists
os.makedirs("screenshots", exist_ok=True)

# Mount the screenshots directory to serve images
app.mount("/screenshots", StaticFiles(directory="screenshots"), name="screenshots")

# Startup event to initialize database indexes
@app.on_event("startup")
async def startup_event():
    """Initialize database indexes on startup"""
    from database import create_indexes
    await create_indexes()

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(scan.router)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Aura Accessibility Scanner API",
        "version": "1.0.0",
        "environment": settings.environment
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "environment": settings.environment
    }