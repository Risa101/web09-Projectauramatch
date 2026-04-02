from sqlalchemy import Column, Integer, String, DECIMAL, Enum, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base


class RecommendationRule(Base):
    __tablename__ = "recommendation_rules"

    rule_id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False)
    face_shape = Column(Enum("oval", "round", "square", "heart", "oblong", "diamond", "triangle", "any"), default="any")
    skin_tone = Column(Enum("fair", "light", "medium", "tan", "dark", "deep", "any"), default="any")
    skin_undertone = Column(Enum("warm", "cool", "neutral", "any"), default="any")
    personal_color = Column(Enum("spring", "summer", "autumn", "winter", "any"), default="any")
    gender = Column(Enum("female", "male", "any"), default="any")
    ethnicity = Column(Enum("asian", "caucasian", "african", "latino",
                            "middle_eastern", "south_asian", "mixed", "any"), default="any")
    priority = Column(Integer, default=0)

    product = relationship("Product")


class Recommendation(Base):
    __tablename__ = "recommendations"

    recommendation_id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(Integer, ForeignKey("analysis_results.analysis_id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False)
    score = Column(DECIMAL(5, 2))
    created_at = Column(DateTime, server_default=func.now())

    analysis = relationship("AnalysisResult", back_populates="recommendations")
    product = relationship("Product")
    feedback = relationship("RecommendationFeedback", back_populates="recommendation")


class RecommendationFeedback(Base):
    __tablename__ = "recommendation_feedback"

    feedback_id = Column(Integer, primary_key=True, autoincrement=True)
    recommendation_id = Column(Integer, ForeignKey("recommendations.recommendation_id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    rating = Column(Enum("like", "dislike"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    recommendation = relationship("Recommendation", back_populates="feedback")
    user = relationship("User", back_populates="recommendation_feedback")


class Favorite(Base):
    __tablename__ = "favorites"

    favorite_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (UniqueConstraint("user_id", "product_id", name="uq_favorite"),)

    user = relationship("User", back_populates="favorites")
    product = relationship("Product", back_populates="favorites")
