from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class StockAvailabilityRequest(BaseModel):
    city: Optional[str] = None
    skus: Optional[List[str]] = None
    page: int = 1
    pageSize: int = 10
    sortBy: Optional[str] = None
    sortOrder: Optional[str] = "ASC"
    dateFrom: Optional[date] = None
    dateTo: Optional[date] = None
    search: str

class SKUData(BaseModel):
    sku: str
    instock_darkstores: int
    instock_darkstores_percentage: float
    total_darkstores: int
    total_stock: int
    days_of_stock: float
    out_of_stock_flag: bool

class StockAvailabilityResponse(BaseModel):
    city: Optional[str] = None
    data: List[SKUData]
