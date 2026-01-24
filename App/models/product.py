# App/models/product.py

from sqlalchemy import Column, String, Float, Boolean, DateTime
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Product(Base):
    __tablename__ = "Products"  # existing table name

    ProductId = Column(UNIQUEIDENTIFIER, primary_key=True)
    NameEn = Column(String(255), nullable=False)
    NameAr = Column(String(255), nullable=True)
    CategoryId = Column(UNIQUEIDENTIFIER, nullable=False)
    CompanyId = Column(UNIQUEIDENTIFIER, nullable=False)
    Description = Column(String, nullable=False)
    MedicalDescription = Column(String, nullable=False)
    Tags = Column(String, nullable=True)
    AverageRating = Column(Float, default=0)
    TotalRatings = Column(Float, default=0)
    DiscountPercentage = Column(Float, default=0)
    ActiveIngredients = Column(String, nullable=False)
    SideEffects = Column(String, nullable=True)
    Contraindications = Column(String, nullable=True)
    Price = Column(Float, default=0)
    IsDeleted = Column(Boolean, default=False)
    IsAvailable = Column(Boolean, default=True)
    DosageForm = Column(String, nullable=True)
    CreatedAt = Column(DateTime, nullable=False)
    UpdatedAt = Column(DateTime, nullable=False)
