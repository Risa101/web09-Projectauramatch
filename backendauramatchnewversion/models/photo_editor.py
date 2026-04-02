from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base


class EditFilter(Base):
    __tablename__ = "edit_filters"

    filter_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    category = Column(Enum("beauty", "color", "light", "vintage", "makeup"), nullable=False)
    thumbnail_url = Column(String(255))
    config = Column(JSON)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now())


class EditSticker(Base):
    __tablename__ = "edit_stickers"

    sticker_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    category = Column(Enum("face", "decoration", "text", "emoji"), nullable=False)
    image_url = Column(String(255))
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now())


class PhotoEdit(Base):
    __tablename__ = "photo_edits"

    edit_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    original_image = Column(String(255))
    edited_image = Column(String(255))
    edit_config = Column(JSON)
    source = Column(Enum("upload", "analysis", "gemini"), default="upload")
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="photo_edits")
