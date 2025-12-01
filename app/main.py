"""
FastAPI Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.v1 import auth, users, parking, washing, shifts
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
from app.api.routes.v1.auth import auth_routes
app.include_router(auth_routes.router, prefix="/api/v1")

from app.api.routes.v1.expenses import expense_routes
app.include_router(expense_routes.router, prefix="/api/v1")

from app.api.routes.v1.shifts import shift_routes
app.include_router(shift_routes.router, prefix="/api/v1")

# app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
# app.include_router(washing.router, prefix="/api/v1/washing", tags=["Washing"])
# app.include_router(shifts.router, prefix="/api/v1/shifts", tags=["Shifts"])

from app.api.routes.v1.parking import parking_routes, rate_routes
app.include_router(parking_routes.router, prefix="/api/v1")
app.include_router(rate_routes.router, prefix="/api/v1/parking")

from app.api.routes.v1.washing import washing_routes
app.include_router(washing_routes.router, prefix="/api/v1/washing")

from app.api.routes.v1.subscriptions import subscription_routes
app.include_router(subscription_routes.router, prefix="/api/v1")

from app.api.routes.v1.agreements import agreement_routes
app.include_router(agreement_routes.router, prefix="/api/v1")

from app.api.routes.v1.notifications import notification_routes
app.include_router(notification_routes.router, prefix="/api/v1")

from app.api.routes.v1 import washers
app.include_router(washers.router, prefix="/api/v1")

from app.api.routes.v1.financial import advance_routes
app.include_router(advance_routes.router, prefix="/api/v1")

from app.api.routes.v1.financial import bonus_routes
app.include_router(bonus_routes.router, prefix="/api/v1/bonuses", tags=["Bonuses"])

from app.api.routes.v1.reports import revenue
app.include_router(revenue.router, prefix="/api/v1/reports")

from app.api.routes.v1.reports import performance
app.include_router(performance.router, prefix="/api/v1/reports", tags=["Reports"])

from app.api.routes.v1.reports import washing_analytics
app.include_router(washing_analytics.router, prefix="/api/v1/reports", tags=["Reports"])

from app.api.routes.v1.reports import agreement_reports_routes
app.include_router(agreement_reports_routes.router, prefix="/api/v1")

from app.api.routes.v1.reports import activity_reports_routes
app.include_router(activity_reports_routes.router, prefix="/api/v1")

from app.api.routes.v1.reports import occupancy_reports_routes
app.include_router(occupancy_reports_routes.router, prefix="/api/v1/reports", tags=["Reports"])

from app.api.routes.v1.reports import dashboard_routes
app.include_router(dashboard_routes.router, prefix="/api/v1/reports", tags=["Reports"])

from app.api.routes.v1.reports import summary_stats_routes
app.include_router(summary_stats_routes.router, prefix="/api/v1/reports")

from app.api.routes.v1.reports import export_routes
app.include_router(export_routes.router, prefix="/api/v1/reports")

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
