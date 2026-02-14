from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List

from app.database.connection import get_db
from app.models.all_models import User, Order, OrderItem, Cart, CartItem, Voucher, VoucherUsage
from app.schemas.all_schemas import OrderResponse, OrderCreate
from app.dependencies.auth_dependency import get_current_user
from datetime import datetime

router = APIRouter()

@router.post("/checkout", response_model=OrderResponse)
async def checkout(
    order_in: OrderCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 1. Get Cart
    result = await db.execute(select(Cart).where(Cart.user_id == user.id).options(selectinload(Cart.items).selectinload(CartItem.product)))
    cart = result.scalars().first()
    
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    # 2. Calculate Total & Validate Stock
    total_amount = 0.0
    order_items_data = []
    
    for item in cart.items:
        if item.product.stock < item.quantity:
             raise HTTPException(status_code=400, detail=f"Not enough stock for {item.product.name}")
        
        price = item.product.price
        total_amount += price * item.quantity
        order_items_data.append({
            "product_id": item.product_id,
            "quantity": item.quantity,
            "price": price
        })

    # 3. Apply Voucher (if any)
    discount_amount = 0.0
    voucher_id = None
    
    if order_in.voucher_code:
        v_result = await db.execute(select(Voucher).where(Voucher.code == order_in.voucher_code))
        voucher = v_result.scalars().first()
        
        if voucher and voucher.is_active:
             # Basic validation (could refactor to share logic with voucher.py)
             if voucher.minimum_spend <= total_amount:
                # Calculate
                if voucher.discount_type == "percentage":
                    discount_amount = total_amount * (voucher.discount_value / 100)
                    if voucher.max_discount_amount:
                        discount_amount = min(discount_amount, voucher.max_discount_amount)
                elif voucher.discount_type == "fixed_amount":
                     discount_amount = voucher.discount_value
                
                discount_amount = min(discount_amount, total_amount)
                voucher_id = voucher.id
                
                # Update voucher usage
                voucher.used_count += 1
                usage = VoucherUsage(voucher_id=voucher.id, user_id=user.id)
                db.add(usage)

    final_amount = total_amount - discount_amount

    # 4. Create Order
    new_order = Order(
        user_id=user.id,
        total_amount=total_amount,
        discount_amount=discount_amount,
        final_amount=final_amount,
        voucher_id=voucher_id,
        status="pending"
    )
    db.add(new_order)
    await db.commit() # Commit to get ID
    await db.refresh(new_order)

    # 5. Create Order Items & Deduct Stock
    for item_data in order_items_data:
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=item_data["product_id"],
            quantity=item_data["quantity"],
            price=item_data["price"]
        )
        db.add(order_item)
        
        # Deduct stock
        prod = await db.get(Product, item_data["product_id"]) # Re-fetch to be safe or use existing ref if attached
        if prod:
            prod.stock -= item_data["quantity"]

    # 6. Clear Cart
    for item in cart.items:
        await db.delete(item)
    
    await db.commit()
    await db.refresh(new_order)
    
    # Re-fetch order with items for response
    # (Optional: or construct response manually if lazy loading is tricky)
    final_order_result = await db.execute(
        select(Order).where(Order.id == new_order.id).options(selectinload(Order.items).selectinload(OrderItem.product))
    )
    return final_order_result.scalars().first()

@router.get("/", response_model=List[OrderResponse])
async def get_orders(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Order).where(Order.user_id == user.id).order_by(Order.created_at.desc()).options(selectinload(Order.items).selectinload(OrderItem.product))
    )
    return result.scalars().all()

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Order).where(Order.id == order_id, Order.user_id == user.id).options(selectinload(Order.items).selectinload(OrderItem.product))
    )
    order = result.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
