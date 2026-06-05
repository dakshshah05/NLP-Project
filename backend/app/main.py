import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import settings
from backend.app.api import dashboard, command, workflows, agents, memory, storage

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Production backend service for AURA AI, translating commands to workflows.",
    version="2.0.0"
)

# CORS origins setup
frontend_url = os.getenv("FRONTEND_URL", "*")
origins = [
    frontend_url,
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if frontend_url != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount APIRouters
app.include_router(dashboard.router, prefix=f"{settings.API_V1_STR}/dashboard", tags=["Dashboard"])
app.include_router(command.router, prefix=f"{settings.API_V1_STR}/command", tags=["Commands"])
app.include_router(workflows.router, prefix=f"{settings.API_V1_STR}/workflows", tags=["Workflows"])
app.include_router(agents.router, prefix=f"{settings.API_V1_STR}/agents", tags=["Agents"])
app.include_router(memory.router, prefix=f"{settings.API_V1_STR}/memory", tags=["Memory"])
app.include_router(storage.router, prefix=f"{settings.API_V1_STR}/storage", tags=["Storage"])

# Render Health Check Endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/")
def read_root():
    return {"message": "Welcome to AURA AI Production API service. Swagger specs at /docs"}
