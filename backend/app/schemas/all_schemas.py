from pydantic import BaseModel, Field, ConfigDict, ConfigDict
from typing import List, Optional
from datetime import datetime
from app.models.all_models import UserRole, OrderStatus, DiscountType

# --- User ---
class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    firebase_uid: str
    full_name: Optional[str] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None

class UserResponse(UserBase):
    id: int
    firebase_uid: str
    role: UserRole
    full_name: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# --- Category ---
class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

# --- Product ---
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    image_url: Optional[str] = None
    category_id: int

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    category: Optional[CategoryResponse] = None
    
    model_config = ConfigDict(from_attributes=True)

# --- Cart ---
class CartItemBase(BaseModel):
    product_id: int
    quantity: int

class CartItemCreate(CartItemBase):
    pass

class CartItemResponse(CartItemBase):
    id: int
    product: ProductResponse
    
    model_config = ConfigDict(from_attributes=True)

class CartResponse(BaseModel):
    id: int
    items: List[CartItemResponse]
    
    model_config = ConfigDict(from_attributes=True)

# --- Voucher ---
class VoucherBase(BaseModel):
    code: str
    description: Optional[str] = None
    discount_type: DiscountType
    discount_value: float
    minimum_spend: float = 0.0
    max_discount_amount: Optional[float] = None
    usage_limit: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: bool = True

class VoucherCreate(VoucherBase):
    pass

class VoucherResponse(VoucherBase):
    id: int
    used_count: int
    
    model_config = ConfigDict(from_attributes=True)

# --- Order ---
class OrderItemResponse(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    price: float

    model_config = ConfigDict(from_attributes=True)

class OrderResponse(BaseModel):
    id: int
    total_amount: float
    discount_amount: float
    final_amount: float
    status: OrderStatus
    created_at: datetime
    items: List[OrderItemResponse]
    
    model_config = ConfigDict(from_attributes=True)

class OrderCreate(BaseModel):
    voucher_code: Optional[str] = None

class VoucherApplyRequest(BaseModel):
    voucher_code: str
    cart_total: float
