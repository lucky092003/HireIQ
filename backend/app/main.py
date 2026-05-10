from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.match import router

app = FastAPI(
    title="HireIQ",
    description="LangChain-powered JD to candidate ranking system",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173"],  # Vite + React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def health():
    return {
        "status": "running",
        "service": "HireIQ",
        "version": "1.0.0"
    }


@app.get("/health")
def detailed_health():
    return {
        "status": "healthy",
        "service": "HireIQ - LangChain Agent",
        "endpoints": {
            "match": "POST /api/hireiq/match"
        }
    }