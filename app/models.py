from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from bson import ObjectId

class User(BaseModel):
    user_id: Optional[str] = Field(default_factory=lambda: str(ObjectId()))
    email: EmailStr
    name: str
    mobile: str

class Expense(BaseModel):
    user_id: str
    description: str
    amount: float
    split_method: str
    splits: dict
