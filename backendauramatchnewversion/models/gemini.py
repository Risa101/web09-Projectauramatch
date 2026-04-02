from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base


class GeminiSession(Base):
    __tablename__ = "gemini_sessions"

    session_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    analysis_id = Column(Integer, ForeignKey("analysis_results.analysis_id", ondelete="SET NULL"), nullable=True)
    title = Column(String(200))
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="gemini_sessions")
    messages = relationship("GeminiMessage", back_populates="session")


class GeminiMessage(Base):
    __tablename__ = "gemini_messages"

    message_id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("gemini_sessions.session_id", ondelete="CASCADE"), nullable=False)
    role = Column(Enum("user", "model"), nullable=False)
    prompt = Column(Text)
    response = Column(Text)
    image_input = Column(String(255))
    image_output = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())

    session = relationship("GeminiSession", back_populates="messages")
