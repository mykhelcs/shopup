from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime

from app.database.connection import get_db
from app.models.all_models import Voucher, User
from app.schemas.all_schemas import VoucherApplyRequest
from app.dependencies.auth_dependency import get_current_user

router = APIRouter()

@router.post("/apply")
async def apply_voucher(
    request: VoucherApplyRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 1. Fetch Voucher
    result = await db.execute(select(Voucher).where(Voucher.code == request.voucher_code))
    voucher = result.scalars().first()
    
    if not voucher:
        raise HTTPException(status_code=404, detail="Voucher not found")
        
    if not voucher.is_active:
        raise HTTPException(status_code=400, detail="Voucher is inactive")

    # 2. Validate Expiry
    now = datetime.now()
    if voucher.start_date and now < voucher.start_date:
        raise HTTPException(status_code=400, detail="Voucher not yet active")
    if voucher.end_date and now > voucher.end_date:
        raise HTTPException(status_code=400, detail="Voucher expired")

    # 3. Validate Usage Limit (Global)
    if voucher.usage_limit is not None and voucher.used_count >= voucher.usage_limit:
        raise HTTPException(status_code=400, detail="Voucher usage limit reached")
    
    # 4. Validate Minimum Spend
    if request.cart_total < voucher.minimum_spend:
        raise HTTPException(status_code=400, detail=f"Minimum spend of {voucher.minimum_spend} required")

    # 5. Calculate Discount
    discount_amount = 0.0
    if voucher.discount_type == "percentage":
        discount_amount = request.cart_total * (voucher.discount_value / 100)
        if voucher.max_discount_amount:
            discount_amount = min(discount_amount, voucher.max_discount_amount)
    elif voucher.discount_type == "fixed_amount":
         discount_amount = voucher.discount_value
    elif voucher.discount_type == "free_shipping":
         # Logic for shipping fee deduction would go here (assuming shipping is separate or part of total)
         # For simplicity, let's say it deducts a fixed shipping cost or just 0 if shipping is free
         discount_amount = 0 # Placeholder implementation
         
    # Ensure discount doesn't exceed total
    discount_amount = min(discount_amount, request.cart_total)
    final_total = request.cart_total - discount_amount

    return {
        "voucher_code": voucher.code,
        "discount_amount": discount_amount,
        "final_total": final_total,
        "message": "Voucher applied successfully"
    }
