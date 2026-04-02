from sqlalchemy import Column, Integer, String, Text, DECIMAL, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base


class ClickLog(Base):
    __tablename__ = "click_logs"

    log_id = Column(Integer, primary_key=True, autoincrement=True)
    link_id = Column(Integer, ForeignKey("product_links.link_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    platform = Column(Enum("shopee", "tiktok", "lazada"), nullable=False)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    clicked_at = Column(DateTime, server_default=func.now())

    link = relationship("ProductLink", back_populates="click_logs")


class Commission(Base):
    __tablename__ = "commissions"

    commission_id = Column(Integer, primary_key=True, autoincrement=True)
    link_id = Column(Integer, ForeignKey("product_links.link_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    platform = Column(Enum("shopee", "tiktok", "lazada"), nullable=False)
    amount = Column(DECIMAL(10, 2))
    status = Column(Enum("pending", "confirmed", "paid"), default="pending")
    clicked_at = Column(DateTime, server_default=func.now())

    link = relationship("ProductLink", back_populates="commissions")
