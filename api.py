from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc
from database import get_db, StockData
from models import StockAvailabilityRequest, StockAvailabilityResponse, SKUData
from typing import Optional, List
import math
from collections import defaultdict

app = FastAPI(title="Stock Availability API", version="1.0.0")

@app.post("/api/stock-availability")
async def get_stock_availability(
    request: StockAvailabilityRequest,
    db: Session = Depends(get_db)
):
    """
    Fetch product stock and listing data for a city with optional filters, pagination, sorting, and search.
    Returns individual SKU data with metrics.
    """
    
    # Extract parameters from request
    city = request.city
    sku_list = request.skus
    page = request.page
    pageSize = request.pageSize
    sortBy = request.sortBy
    sortOrder = request.sortOrder
    dateFrom = request.dateFrom
    dateTo = request.dateTo
    search = request.search
    
    # Build query
    query = db.query(StockData)
    
    # Apply filters
    filters = []
    
    if city:
        filters.append(StockData.city_name == city)
    
    if sku_list:
        filters.append(StockData.product_id.in_(sku_list))
    
    if dateFrom:
        filters.append(StockData.date >= dateFrom)
    
    if dateTo:
        filters.append(StockData.date <= dateTo)
    
    if search:
        search_filter = or_(
            StockData.product_name.ilike(f"%{search}%"),
            StockData.product_id.ilike(f"%{search}%"),
            StockData.category.ilike(f"%{search}%")
        )
        filters.append(search_filter)
    
    if filters:
        query = query.filter(and_(*filters))
    
    # Execute query to get all matching records
    results = query.all()
    
    if not results:
        return StockAvailabilityResponse(
            city=city,
            data=[]
        )
    
    # Group data by SKU and calculate metrics for each SKU
    sku_data = defaultdict(lambda: {
        'records': [],
        'total_stock': 0,
        'total_instock_darkstores': 0,
        'total_total_darkstores': 0,
        'total_sales': 0,
        'record_count': 0
    })
    
    for record in results:
        sku = record.product_id
        sku_data[sku]['records'].append(record)
        sku_data[sku]['total_stock'] += record.stock_quantity
        sku_data[sku]['total_instock_darkstores'] += record.instock_darkstores
        sku_data[sku]['total_total_darkstores'] += record.total_darkstores
        sku_data[sku]['total_sales'] += record.total_sales
        sku_data[sku]['record_count'] += 1
    
    # Create SKU data list
    sku_list_data = []
    for sku, data in sku_data.items():
        record_count = data['record_count']
        
        # Calculate averages
        avg_instock_darkstores = data['total_instock_darkstores'] / record_count
        avg_total_darkstores = data['total_total_darkstores'] / record_count
        avg_daily_sales = data['total_sales'] / record_count
        
        # Calculate metrics
        total_stock = data['total_stock']
        instock_percentage = (avg_instock_darkstores / avg_total_darkstores * 100) if avg_total_darkstores > 0 else 0
        days_of_stock = total_stock / avg_daily_sales if avg_daily_sales > 0 else 0
        out_of_stock_flag = total_stock == 0
        
        sku_data_item = SKUData(
            sku=sku,
            instock_darkstores=int(round(avg_instock_darkstores)),
            instock_darkstores_percentage=round(instock_percentage, 2),
            total_darkstores=int(round(avg_total_darkstores)),
            total_stock=total_stock,
            days_of_stock=round(days_of_stock, 2),
            out_of_stock_flag=out_of_stock_flag
        )
        sku_list_data.append(sku_data_item)
    
    # Apply sorting
    if sortBy:
        if sortBy.upper() == "TOTAL STOCK":
            sku_list_data.sort(key=lambda x: x.total_stock, reverse=(sortOrder.upper() == "DESC"))
        elif sortBy.upper() == "INSTOCK DARKSTORES":
            sku_list_data.sort(key=lambda x: x.instock_darkstores, reverse=(sortOrder.upper() == "DESC"))
        elif sortBy.upper() == "TOTAL DARKSTORES":
            sku_list_data.sort(key=lambda x: x.total_darkstores, reverse=(sortOrder.upper() == "DESC"))
        elif sortBy.upper() == "DAYS OF STOCK":
            sku_list_data.sort(key=lambda x: x.days_of_stock, reverse=(sortOrder.upper() == "DESC"))
        elif sortBy.upper() == "SKU":
            sku_list_data.sort(key=lambda x: x.sku, reverse=(sortOrder.upper() == "DESC"))
    
    # Apply pagination
    start_idx = (page - 1) * pageSize
    end_idx = start_idx + pageSize
    paginated_data = sku_list_data[start_idx:end_idx]
    
    return StockAvailabilityResponse(
        city=city,
        data=paginated_data
    )

@app.get("/")
async def root():
    return {"message": "Stock Availability API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
