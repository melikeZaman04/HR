import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.presentation.api.v1.routes.scenarios import router as scenarios_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

app = FastAPI(
    title="HireSync AI",
    description="Multi-Agent Hiring Decision System — Strategy, Culture, Salary, Question agents",
    version="2.0.0",
)

# CORS middleware for browser requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/dashboard")


@app.get("/health", tags=["system"])
def health_check():
    return {"status": "healthy", "service": "HireSync AI"}


app.include_router(scenarios_router, prefix="/api/v1", tags=["scenarios"])

# Serve the agent dashboard at /dashboard
app.mount("/dashboard", StaticFiles(directory="static", html=True), name="dashboard")
