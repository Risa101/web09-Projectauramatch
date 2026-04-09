import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from config.database import engine, Base
from config.redis_config import check_redis_health
from config.chromadb_config import check_chromadb_health

logger = logging.getLogger(__name__)

# Import all models to register them
import models.user
import models.misc
import models.product
import models.analysis
import models.recommendation
import models.commission
import models.gemini
import models.photo_editor
import models.blog
import models.behavior
import models.saved_look

# Import routes
from routes import auth, products, analysis, recommendations, gemini, commission, profile, landmarks, behavior, saved_looks, favorites, skin_concerns, reviews, blog, banner

# Create tables
Base.metadata.create_all(bind=engine)

# Create upload directory
os.makedirs("uploads", exist_ok=True)

app = FastAPI(
    title="AuraMatch API",
    description="Web Application for Facial Structure and Personal Color Analysis",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5175", "http://localhost:5177", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files (uploads)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Routers
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(analysis.router)
app.include_router(recommendations.router)
app.include_router(gemini.router)
app.include_router(commission.router)
app.include_router(profile.router)
app.include_router(landmarks.router)
app.include_router(behavior.router)
app.include_router(saved_looks.router)
app.include_router(favorites.router)
app.include_router(skin_concerns.router)
app.include_router(reviews.router)
app.include_router(blog.router)
app.include_router(banner.router)


@app.on_event("startup")
def startup_event():
    redis_status = check_redis_health()
    if redis_status["status"] == "connected":
        logger.info("Redis connected at %s:%s", redis_status["host"], redis_status["port"])
    else:
        logger.warning("Redis: %s", redis_status["message"])

    chroma_status = check_chromadb_health()
    if chroma_status["status"] == "connected":
        logger.info(
            "ChromaDB: %d products indexed at %s",
            chroma_status["product_count"],
            chroma_status["path"],
        )
    else:
        logger.warning("ChromaDB: %s (TF-IDF fallback active)", chroma_status["message"])


@app.get("/")
def root():
    return {"message": "AuraMatch API is running", "docs": "/docs"}
