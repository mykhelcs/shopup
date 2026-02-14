from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List

from app.database.connection import get_db
from app.models.all_models import User, Cart, CartItem, Product
from app.schemas.all_schemas import CartResponse, CartItemCreate, CartItemResponse
from app.dependencies.auth_dependency import get_current_user

router = APIRouter()

async def get_or_create_cart(user: User, db: AsyncSession) -> Cart:
    # Check if user has a cart
    result = await db.execute(
        select(Cart).where(Cart.user_id == user.id).options(selectinload(Cart.items).selectinload(CartItem.product))
    )
    cart = result.scalars().first()
    
    if not cart:
        cart = Cart(user_id=user.id)
        db.add(cart)
        await db.commit()
        await db.refresh(cart)
        # Re-fetch with relationships to avoid lazy load issues in async
        result = await db.execute(
            select(Cart).where(Cart.id == cart.id).options(selectinload(Cart.items).selectinload(CartItem.product))
        )
        cart = result.scalars().first()
        
    return cart

@router.get("/", response_model=CartResponse)
async def get_cart(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    cart = await get_or_create_cart(user, db)
    return cart

@router.post("/add")
async def add_to_cart(
    item_in: CartItemCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    cart = await get_or_create_cart(user, db)
    
    # Check product validity
    prod_result = await db.execute(select(Product).where(Product.id == item_in.product_id))
    product = prod_result.scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    if product.stock < item_in.quantity:
        raise HTTPException(status_code=400, detail="Not enough stock")

    # Check if item exists in cart
    existing_item_result = await db.execute(
        select(CartItem).where(CartItem.cart_id == cart.id, CartItem.product_id == item_in.product_id)
    )
    existing_item = existing_item_result.scalars().first()

    if existing_item:
        existing_item.quantity += item_in.quantity
    else:
        new_item = CartItem(
            cart_id=cart.id,
            product_id=item_in.product_id,
            quantity=item_in.quantity
        )
        db.add(new_item)
    
    await db.commit()
    return {"message": "Item added to cart"}


@router.delete("/remove/{product_id}")
async def remove_from_cart(
    product_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    cart = await get_or_create_cart(user, db)
    
    result = await db.execute(
        select(CartItem).where(CartItem.cart_id == cart.id, CartItem.product_id == product_id)
    )
    item = result.scalars().first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not in cart")
        
    await db.delete(item)
    await db.commit()
    return {"message": "Item removed from cart"}

@router.put("/update")
async def update_cart_quantity(
    item_in: CartItemCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    cart = await get_or_create_cart(user, db)
    
    result = await db.execute(
        select(CartItem).where(CartItem.cart_id == cart.id, CartItem.product_id == item_in.product_id)
    )
    item = result.scalars().first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not in cart")
    
    if item_in.quantity <= 0:
        await db.delete(item)
    else:
        # Check stock
        prod_result = await db.execute(select(Product).where(Product.id == item_in.product_id))
        product = prod_result.scalars().first()
        if product.stock < item_in.quantity:
             raise HTTPException(status_code=400, detail="Not enough stock")
        item.quantity = item_in.quantity
        
    await db.commit()
    return {"message": "Cart updated"}
