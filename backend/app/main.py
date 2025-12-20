from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.config import get_settings
from app.database import get_db_session
from app.api import workers, jobs, events
from app.auth import routes as auth_routes
from app.services.event_indexer import EventIndexer
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title="GalaxyRend Backend API",
    description="Backend service for GalaxyRend decentralized computing platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_routes.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(workers.router, prefix="/api/v1/workers", tags=["workers"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["jobs"])
app.include_router(events.router, prefix="/api/v1/events", tags=["events"])

# Hybrid API endpoints (Graph + Database)
from app.api import hybrid
app.include_router(hybrid.router, prefix="/api/v1/hybrid", tags=["hybrid-graph"])

# Global event indexer instance
event_indexer = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global event_indexer
    logger.info("Starting GalaxyRend Backend API...")
    
    # Initialize database
    from app.database import init_db
    await init_db()
    
    # Start event indexer
    if settings.enable_event_indexing:
        logger.info("Starting event indexer...")
        event_indexer = EventIndexer()
        asyncio.create_task(event_indexer.start())
    
    logger.info("GalaxyRend Backend API started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown"""
    global event_indexer
    logger.info("Shutting down GalaxyRend Backend API...")
    
    if event_indexer:
        await event_indexer.stop()
    
    logger.info("GalaxyRend Backend API stopped")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "GalaxyRend Backend API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "indexer": "running" if event_indexer and event_indexer.is_running else "stopped",
        "settings": {
            "contract_address": settings.contract_address,
            "rpc_url": settings.starknet_rpc_url,
            "network": settings.network
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
