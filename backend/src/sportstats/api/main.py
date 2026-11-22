"""FastAPI Application Entrypoint for SportStats."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from sportstats import __version__
from sportstats.api.routers import (
    admin,
    ai,
    analytics,
    editions,
    participants,
    sources,
    sports,
    tournaments,
)
from sportstats.api.static_ui import HTML_DASHBOARD
from sportstats.config import settings

app = FastAPI(
    title="SportStats API",
    description="Multi-sport statistical framework and AI-assisted performance tracker",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/v1/openapi.json",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse, tags=["Dashboard"], include_in_schema=False)
@app.get("/dashboard", response_class=HTMLResponse, tags=["Dashboard"], include_in_schema=False)
def serve_dashboard():
    """Serve the interactive SportStats web dashboard directly."""
    return HTMLResponse(content=HTML_DASHBOARD)


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint for container orchestrators and load balancers."""
    return {
        "status": "healthy",
        "app": "sportstats",
        "version": __version__,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/api/v1/health", tags=["Health"])
def api_v1_health_check():
    """Versioned health check endpoint."""
    return {
        "status": "healthy",
        "app": "sportstats",
        "api_version": "v1",
        "version": __version__,
    }


# Include Routers under /api/v1
app.include_router(sports.router, prefix="/api/v1")
app.include_router(tournaments.router, prefix="/api/v1")
app.include_router(editions.router, prefix="/api/v1")
app.include_router(participants.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(sources.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")
