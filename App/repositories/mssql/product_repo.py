from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from App.models.product import Product  # your SQLAlchemy Product model
from App.repositories.mssql.connection import get_session
from App.schemas.drug import DrugSchema


class ProductRepository:
    """Repository for Products table using SQLAlchemy ORM"""

    def get_products_for_sync(self, last_sync: Optional[datetime] = None) -> List[DrugSchema]:
        """
        Retrieve products updated or created since `last_sync`.
        If `last_sync` is None, retrieves all products.

        Args:
            last_sync (datetime, optional): Last sync timestamp.

        Returns:
            List[DrugSchema]: List of products for syncing.
        """
        session: Session = get_session()
        try:
            query = session.query(Product)

            if last_sync:
                query = query.filter(
                    (Product.CreatedAt >= last_sync) | (Product.UpdatedAt >= last_sync)
                )

            products = query.all()

            # Convert ORM objects to Pydantic schemas
            return [
                DrugSchema(
                    ProductId=str(p.ProductId),
                    NameEn=p.NameEn,
                    NameAr=p.NameAr,
                    CategoryId=str(p.CategoryId),
                    CompanyId=str(p.CompanyId),
                    Description=p.Description,
                    MedicalDescription=p.MedicalDescription,
                    Tags=p.Tags,
                    AverageRating=float(p.AverageRating or 0),
                    TotalRatings=int(p.TotalRatings or 0),
                    DiscountPercentage=float(p.DiscountPercentage or 0),
                    ActiveIngredients=p.ActiveIngredients,
                    SideEffects=p.SideEffects,
                    Contraindications=p.Contraindications,
                    Price=float(p.Price or 0),
                    IsDeleted=bool(p.IsDeleted),
                    IsAvailable=bool(p.IsAvailable),
                    DosageForm=p.DosageForm,
                    CreatedAt=p.CreatedAt,
                    UpdatedAt=p.UpdatedAt,
                )
                for p in products
            ]

        finally:
            session.close()
