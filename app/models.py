from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict

class User(BaseModel):
    id: str
    name: str
    email: EmailStr
    mobile: str

class Expense(BaseModel):
    id: str
    payer: str
    amount: float
    participants: List[str]
    split_method: str
    splits: Optional[Dict[str, float]]  # Dictionary to store user ID and the amount they owe
