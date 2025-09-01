from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, Literal
from datetime import datetime

class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None

class UserCreate(UserBase):
    wallet_balance: Optional[float] = 0.0

class UserOut(UserBase):
    id: int
    wallet_balance: float

    model_config = ConfigDict(from_attributes=True)

class WalletUpdateIn(BaseModel):
    amount: float = Field(..., gt=0, description="Positive amount")
    mode: Literal["credit", "debit", "set"] = "credit"
    description: Optional[str] = None

class TransactionOut(BaseModel):
    id: int
    user_id: int
    amount: float
    type: str
    description: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
