from sqlalchemy import Column, Integer, String, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum("admin", "user"), default="user")
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now())

    profile = relationship("UserProfile", back_populates="user", uselist=False)
    analysis_results = relationship("AnalysisResult", back_populates="user")
    favorites = relationship("Favorite", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    gemini_sessions = relationship("GeminiSession", back_populates="user")
    blog_posts = relationship("BlogPost", back_populates="author")
    photo_edits = relationship("PhotoEdit", back_populates="user")
    reviews = relationship("ProductReview", back_populates="user")
    recommendation_feedback = relationship("RecommendationFeedback", back_populates="user")
    search_history = relationship("SearchHistory", back_populates="user")
