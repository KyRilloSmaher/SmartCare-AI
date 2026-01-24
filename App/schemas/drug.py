
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DrugSchema(BaseModel):
    ProductId: str
    NameEn: str
    NameAr: Optional[str]
    CategoryId: str
    CompanyId: str
    Description: str
    MedicalDescription: str
    Tags: str
    AverageRating: float
    TotalRatings: int
    DiscountPercentage: float
    ActiveIngredients: str
    SideEffects: Optional[str]
    Contraindications: Optional[str]
    Price: float
    IsDeleted: bool
    IsAvailable: bool
    DosageForm: Optional[str]
    CreatedAt: datetime
    UpdatedAt: datetime
