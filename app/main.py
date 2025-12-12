"""
FastAPI application entry point.
Configures and initializes the API server.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from pathlib import Path
from app.config import settings
from app.database import db_manager
from app.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    await db_manager.connect_to_database()
    yield
    # Shutdown
    await db_manager.close_database_connection()


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Multi-tenant organization management service with dynamic collection creation",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, tags=["Organization Management"])

# Mount static files for frontend
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path), html=True), name="static")


@app.get("/", tags=["Frontend"])
async def serve_frontend():
    """Serve the frontend application."""
    frontend_file = frontend_path / "index.html"
    if frontend_file.exists():
        from fastapi.responses import HTMLResponse
        with open(frontend_file, 'r', encoding='utf-8') as f:
            content = f.read()
        return HTMLResponse(content=content, headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        })
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


# Serve CSS and JS files directly with no-cache headers
@app.get("/style.css", tags=["Frontend"])
async def serve_css():
    """Serve CSS file with no-cache headers."""
    css_file = frontend_path / "style.css"
    if css_file.exists():
        return FileResponse(
            str(css_file),
            media_type="text/css",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )


@app.get("/script.js", tags=["Frontend"])
async def serve_js():
    """Serve JavaScript file with no-cache headers."""
    js_file = frontend_path / "script.js"
    if js_file.exists():
        return FileResponse(
            str(js_file),
            media_type="application/javascript",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )


@app.get("/api", tags=["Health"])
async def root():
    """API root endpoint - health check."""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected" if db_manager.client else "disconnected"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
