"""Versioned API router."""

from fastapi import APIRouter

from app.api.v1.admin import router as admin_router
from app.api.v1.chat import router as chat_router
from app.api.v1.embed import router as embed_router

router = APIRouter(prefix="/api/v1")
router.include_router(admin_router)
router.include_router(chat_router)
router.include_router(embed_router)
