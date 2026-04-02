from sqlalchemy import Column, Integer, String, Text, DECIMAL, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base


class Brand(Base):
    __tablename__ = "brands"

    brand_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    logo_url = Column(String(255))
    website_url = Column(String(255))
    description = Column(Text)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now())

    products = relationship("Product", back_populates="brand")


class ProductCategory(Base):
    __tablename__ = "product_categories"

    category_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    icon_url = Column(String(255))

    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, autoincrement=True)
    brand_id = Column(Integer, ForeignKey("brands.brand_id", ondelete="SET NULL"), nullable=True)
    category_id = Column(Integer, ForeignKey("product_categories.category_id", ondelete="SET NULL"), nullable=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    price = Column(DECIMAL(10, 2))
    image_url = Column(String(255))
    personal_color = Column(String(50), nullable=True)  # spring,summer,autumn,winter (comma-separated)
    commission_rate = Column(DECIMAL(5, 2), default=0)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now())

    brand = relationship("Brand", back_populates="products")
    category = relationship("ProductCategory", back_populates="products")
    links = relationship("ProductLink", back_populates="product")
    color_shades = relationship("ProductColorShade", back_populates="product")
    reviews = relationship("ProductReview", back_populates="product")
    favorites = relationship("Favorite", back_populates="product")


class ProductLink(Base):
    __tablename__ = "product_links"

    link_id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False)
    platform = Column(Enum("shopee", "tiktok", "lazada", "sephora", "watsons", "ulta"), nullable=False)
    url = Column(String(500), nullable=False)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now())

    product = relationship("Product", back_populates="links")
    click_logs = relationship("ClickLog", back_populates="link")
    commissions = relationship("Commission", back_populates="link")


class ProductTag(Base):
    __tablename__ = "product_tags"

    tag_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)


class ProductTagMap(Base):
    __tablename__ = "product_tag_map"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False)
    tag_id = Column(Integer, ForeignKey("product_tags.tag_id", ondelete="CASCADE"), nullable=False)

    product = relationship("Product")
    tag = relationship("ProductTag")


class ProductColorShade(Base):
    __tablename__ = "product_color_shades"

    shade_id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False)
    shade_name = Column(String(100))
    shade_code = Column(String(20))
    hex_color = Column(String(7))
    image_url = Column(String(255))
    is_active = Column(Integer, default=1)

    product = relationship("Product", back_populates="color_shades")
