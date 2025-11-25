"""
FastAPI Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="PMS - Parking & Car Wash Management System API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
# app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
# app.include_router(parking.router, prefix="/api/v1/parking", tags=["Parking"])
# app.include_router(washing.router, prefix="/api/v1/washing", tags=["Washing"])
# app.include_router(shifts.router, prefix="/api/v1/shifts", tags=["Shifts"])
from app.api.routes.v1 import washers, auth

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(washers.router, prefix="/api/v1/washing")

@app.get("/")
async def root():
    return {
        "message": "PMS API - Parking & Car Wash Management System",
        "version": settings.VERSION,
        "docs": "/api/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
