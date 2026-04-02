from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey, DateTime, JSON, Date, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    profile_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    display_name = Column(String(100))
    avatar_url = Column(String(255))
    birth_date = Column(Date)
    gender = Column(Enum("female", "male", "non_binary", "prefer_not_to_say"))
    nationality = Column(String(100))
    bio = Column(Text)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="profile")


class PasswordReset(Base):
    __tablename__ = "password_resets"

    reset_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class SkinConcern(Base):
    __tablename__ = "skin_concerns"

    concern_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    icon_url = Column(String(255))


class UserSkinConcern(Base):
    __tablename__ = "user_skin_concerns"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    concern_id = Column(Integer, ForeignKey("skin_concerns.concern_id"), nullable=False)
    severity = Column(Enum("mild", "moderate", "severe"), default="mild")
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User")
    concern = relationship("SkinConcern")


class ProductConcern(Base):
    __tablename__ = "product_concerns"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False)
    concern_id = Column(Integer, ForeignKey("skin_concerns.concern_id"), nullable=False)

    product = relationship("Product")
    concern = relationship("SkinConcern")


class ProductReview(Base):
    __tablename__ = "product_reviews"

    review_id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text)
    image_url = Column(String(255))
    platform = Column(Enum("shopee", "tiktok", "lazada", "other"))
    is_verified = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())

    product = relationship("Product", back_populates="reviews")
    user = relationship("User", back_populates="reviews")


class Notification(Base):
    __tablename__ = "notifications"

    notification_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text)
    type = Column(Enum("recommendation", "promotion", "system", "review"), default="system")
    is_read = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="notifications")


class Banner(Base):
    __tablename__ = "banners"

    banner_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200))
    image_url = Column(String(255), nullable=False)
    link_url = Column(String(500))
    position = Column(Enum("home_top", "home_middle", "sidebar"), default="home_top")
    starts_at = Column(DateTime)
    ends_at = Column(DateTime)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now())


class SearchHistory(Base):
    __tablename__ = "search_history"

    search_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    keyword = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="search_history")


class AdminLog(Base):
    __tablename__ = "admin_logs"

    log_id = Column(Integer, primary_key=True, autoincrement=True)
    admin_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    action = Column(String(100), nullable=False)
    table_name = Column(String(100))
    record_id = Column(Integer)
    old_value = Column(JSON)
    new_value = Column(JSON)
    ip_address = Column(String(45))
    created_at = Column(DateTime, server_default=func.now())

    admin = relationship("User")
