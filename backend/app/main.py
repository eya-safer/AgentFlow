
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes.approvals import router as approvals_router
from backend.app.api.routes.chat import router as chat_router
from backend.app.api.routes.health import router as health_router
from backend.app.database.connection import Base, engine
from backend.app.database import models


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables when the application starts
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="AgentFlow API",
    description="AI-powered Business Assistant",
    version="1.0.0",
    lifespan=lifespan
)

# Allow communication with the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    health_router,
    prefix="/health",
    tags=["Health"]
)

app.include_router(approvals_router)
app.include_router(chat_router)


@app.get("/")
def home():
    return {
        "message": "Welcome to AgentFlow!",
        "status": "running"
    }
