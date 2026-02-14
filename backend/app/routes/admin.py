from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.connection import get_db
from app.models.all_models import User, Product, Voucher
from app.schemas.all_schemas import ProductCreate, ProductResponse, VoucherCreate, VoucherResponse
from app.dependencies.auth_dependency import get_current_admin

router = APIRouter()

# --- Product Management ---
@router.post("/products", response_model=ProductResponse)
async def create_product(
    product_in: ProductCreate,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    new_product = Product(**product_in.dict())
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    return new_product

@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_in: ProductCreate,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    for key, value in product_in.dict().items():
        setattr(product, key, value)
        
    await db.commit()
    await db.refresh(product)
    return product

@router.delete("/products/{product_id}")
async def delete_product(
    product_id: int,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    await db.delete(product)
    await db.commit()
    return {"message": "Product deleted"}

# --- Voucher Management ---
@router.post("/vouchers", response_model=VoucherResponse)
async def create_voucher(
    voucher_in: VoucherCreate,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    new_voucher = Voucher(**voucher_in.dict())
    db.add(new_voucher)
    await db.commit()
    await db.refresh(new_voucher)
    return new_voucher
