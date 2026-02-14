from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from app.database.connection import get_db
from app.models.all_models import Product, Category, Voucher
from app.schemas.all_schemas import ProductResponse, CategoryResponse, VoucherResponse

router = APIRouter()

@router.get("/products", response_model=List[ProductResponse])
async def get_products(
    skip: int = 0, 
    limit: int = 20, 
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Product)
    
    if category_id:
        query = query.where(Product.category_id == category_id)
    
    if search:
        query = query.where(Product.name.ilike(f"%{search}%"))
        
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.get("/categories", response_model=List[CategoryResponse])
async def get_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category))
    return result.scalars().all()

@router.get("/vouchers/active", response_model=List[VoucherResponse])
async def get_active_vouchers(db: AsyncSession = Depends(get_db)):
    # Simple check for now, can be expanded for date range
    result = await db.execute(select(Voucher).where(Voucher.is_active == True))
    return result.scalars().all()
