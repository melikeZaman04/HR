from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.presentation.api.v1.routes.scenarios import router as scenarios_router

app = FastAPI(
    title="AI Decision Ecosystem Engine",
    description="Multi-Agent Decision Support System with CEO, CFO, HR agents",
    version="1.0.0",
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
    """Redirect root to Swagger UI"""
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["system"])
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "AI Decision Ecosystem Engine"}


app.include_router(scenarios_router, prefix="/api/v1", tags=["scenarios"])
