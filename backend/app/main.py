from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.api.router import router
import app.models  # Ensures all ORM models are registered with Base.metadata

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="GossipNet API",
    description="Authoritative backend engine for GossipNet detective game",
    version="1.0.0"
)

# CORS middleware for local dev / frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8000", "http://127.0.0.1:8000", "*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.get("/")
def root():
    return {
        "title": "GossipNet API",
        "tagline": "You were right. Unfortunately, you're wrong.",
        "phase": 1,
        "mode": "DETECTIVE"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
