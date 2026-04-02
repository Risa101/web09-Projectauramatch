from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base


class SavedLook(Base):
    __tablename__ = "saved_looks"

    look_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=True)  # กลางวัน, กลางคืน, ปาร์ตี้, ทำงาน, อื่นๆ
    makeup_data = Column(JSON, nullable=False)  # เก็บ makeup state ทั้งหมด
    filter_data = Column(JSON, nullable=True)  # เก็บ filter + brightness/contrast/saturation
    thumbnail_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User")
