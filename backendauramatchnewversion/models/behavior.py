from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from config.database import Base


class UserBehavior(Base):
    __tablename__ = "user_behaviors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    session_id = Column(String(100), nullable=True)
    event_type = Column(String(50), nullable=False)  # product_view, search, filter, click, similar_view, makeup_select, preset_apply
    event_data = Column(JSON, nullable=True)  # รายละเอียดเพิ่มเติม
    page = Column(String(50), nullable=True)  # products, editor, analyze
    created_at = Column(DateTime, server_default=func.now())
