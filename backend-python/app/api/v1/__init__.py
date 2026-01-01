"""
API v1 Router - combines all endpoint routers
"""

from fastapi import APIRouter

from app.api.v1 import chatbot, auth, outbreaks, alerts, stats, reports
from app.api.v1 import predictions_enhanced  # Enhanced AI predictions
from app.api.v1 import auth_doctor, doctor_station, public_outbreaks, approval, pdf_reports, analytics, export
# from app.api.v1 import admin_init  # DISABLED - security module missing


api_router = APIRouter()

# Include all route modules
api_router.include_router(chatbot.router)
api_router.include_router(auth.router)
api_router.include_router(outbreaks.router)
api_router.include_router(predictions_enhanced.router)  # Enhanced predictions
api_router.include_router(alerts.router)
api_router.include_router(stats.router)
api_router.include_router(reports.router)

# Doctor Station
api_router.include_router(auth_doctor.router)
api_router.include_router(doctor_station.router)

# Admin Approval Workflow
api_router.include_router(approval.router)

# PDF Reports
api_router.include_router(pdf_reports.router)

# Analytics
api_router.include_router(analytics.router)

# CSV Export
api_router.include_router(export.router)

# Public outbreaks (includes doctor data)
api_router.include_router(public_outbreaks.router)

# api_router.include_router(admin_init.router)  # DISABLED




