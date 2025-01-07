# app/main.py

from fastapi import FastAPI,Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
from redis.asyncio import Redis
from contextlib import asynccontextmanager
from app.database import engine, Base
from app.config import settings
from app.utils import logger
from app.routers import (
    auth_router,
    task_router,
    notification_router,
    api_key_router,
    automation_router,
    dependency_router,
    recurrence_router
)

# Create the FastAPI application
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    print("Starting up the application...")
    redis = Redis.from_url("redis://localhost", decode_responses=True)
    await FastAPILimiter.init(redis)
    Base.metadata.create_all(bind=engine)
    try:
        yield
    finally:
        print("Shutting down the application...")

app = FastAPI(
    title=settings.APP_NAME,
    description="An API to manage tasks",
    version="1.0.0",
    debug=settings.DEBUG,  # Enable debug mode if in development
    lifespan=lifespan,
)

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(task_router, prefix="/tasks", tags=["Task"])
app.include_router(recurrence_router, prefix="/recurring-tasks", tags=["Recurring Tasks"])
app.include_router(dependency_router, prefix="/dependent-tasks", tags=["Dependents Task"])
app.include_router(automation_router, prefix="/automation", tags=["Automation"])
app.include_router(notification_router, prefix="/notification", tags=["Notification"])
app.include_router(api_key_router, prefix="/api-key", tags=["API Key"])

# Middleware
@app.middleware("http")
async def log_requests_and_api_key_usage(request: Request, call_next):
    endpoint = request.url.path
    method = request.method
    client_ip = request.client.host
    token = request.headers.get("Authorization")

    logger.info(f"Request: {method} {endpoint} from {client_ip}")
    if token:
        logger.info(f"API key used: {token.split()[1]}")

    response = await call_next(request)
    logger.info(f"Response: {method} {endpoint} returned {response.status_code}")
    return response


# Root endpoint for health check
@app.get("/")
def read_root():
    return {"message": f"{settings.APP_NAME} is running"}
