from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from config.database import engine, Base
import os

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
from routes import auth, products, analysis, recommendations, gemini, commission, profile, landmarks, behavior, saved_looks

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


@app.get("/")
def root():
    return {"message": "AuraMatch API is running", "docs": "/docs"}
