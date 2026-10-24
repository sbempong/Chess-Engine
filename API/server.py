from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .endpoints import router
import uvicorn

def create_app() -> FastAPI:
    app = FastAPI(
        title="Chess Engine API",
        description="REST API for chess engine operations",
        version="1.0.0"
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(router, prefix="/api/v1")
    
    return app

app = create_app()

if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8000)
