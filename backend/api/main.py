"""
FastAPI REST API Server for Ether Clinic Staff Dashboard.
Connects to the same Neon PostgreSQL database as the voice agent.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import sys
import os
from pathlib import Path

# Setup Python path - agent-python must be FIRST so its imports work correctly
current_dir = Path(__file__).parent
backend_dir = current_dir.parent
agent_python_dir = backend_dir / "agent-python"
sys.path.insert(0, str(agent_python_dir))  # agent-python first for its own imports

# Now add current api directory for our modules
os.chdir(str(current_dir))  # Change working directory to api folder

# Import routes (these use relative imports within api folder)
from routes.patients import router as patients_router
from routes.appointments import router as appointments_router
from routes.clinic import router as clinic_router
from routes.staff import router as staff_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Ether Clinic API",
    description="REST API for clinic staff dashboard - manages patients, appointments, and clinic operations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Get allowed origins from environment variable or use defaults
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",") if os.getenv("ALLOWED_ORIGINS") else [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:8080",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:8080",
]

logger.info(f"Allowed CORS origins: {ALLOWED_ORIGINS}")

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(patients_router)
app.include_router(appointments_router)
app.include_router(clinic_router)
app.include_router(staff_router)


@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "message": "Ether Clinic API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "ether-clinic-api"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for better error responses."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error occurred"}
    )


if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Starting Ether Clinic API Server...")
    logger.info("📚 API Documentation available at: http://localhost:8000/docs")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload during development
        log_level="info"
    )
