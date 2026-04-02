from sqlalchemy import Column, Integer, String, Text, DECIMAL, Enum, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base


class ColorPalette(Base):
    __tablename__ = "color_palettes"

    palette_id = Column(Integer, primary_key=True, autoincrement=True)
    season = Column(Enum("spring", "summer", "autumn", "winter"), nullable=False)
    sub_type = Column(String(50))
    description = Column(Text)
    best_colors = Column(JSON)
    avoid_colors = Column(JSON)
    makeup_tips = Column(Text)
    created_at = Column(DateTime, server_default=func.now())


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    analysis_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    image_path = Column(String(255))
    gender = Column(Enum("female", "male", "non_binary"))
    ethnicity = Column(Enum("asian", "caucasian", "african", "latino",
                            "middle_eastern", "south_asian", "mixed", "other"))
    nationality = Column(String(100))
    face_shape = Column(Enum("oval", "round", "square", "heart", "oblong", "diamond", "triangle"))
    skin_tone = Column(Enum("fair", "light", "medium", "tan", "dark", "deep"))
    skin_undertone = Column(Enum("warm", "cool", "neutral"))
    personal_color = Column(Enum("spring", "summer", "autumn", "winter"))
    palette_id = Column(Integer, ForeignKey("color_palettes.palette_id"), nullable=True)
    confidence_score = Column(DECIMAL(5, 2))
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="analysis_results")
    palette = relationship("ColorPalette")
    recommendations = relationship("Recommendation", back_populates="analysis")
    reviews = relationship("AnalysisReview", back_populates="analysis")


class AnalysisReview(Base):
    __tablename__ = "analysis_reviews"

    review_id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(Integer, ForeignKey("analysis_results.analysis_id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    is_accurate = Column(Integer)
    comment = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    analysis = relationship("AnalysisResult", back_populates="reviews")
    user = relationship("User")
