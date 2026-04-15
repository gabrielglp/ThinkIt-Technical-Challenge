from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.presentation.routers import orders, metrics

app = FastAPI(
    title="Orders Management API",
    description="API REST para gestão de pedidos do e-commerce",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(orders.router, prefix="/orders", tags=["orders"])
app.include_router(metrics.router, prefix="/metrics", tags=["metrics"])


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
