from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.chat import router as chat_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Enterprise HCP AI CRM Backend",
    version="0.1.0"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(chat_router)

@app.get("/")
async def root():
    return {
        "status": "running",
        "project": settings.PROJECT_NAME
    }

@app.get("/health")
async def health():
    return {
        "backend": "healthy"
    }
