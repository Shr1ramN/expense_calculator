from fastapi import APIRouter, HTTPException
from app.models import Expense
from app.database import db

router = APIRouter()

@router.post("/expenses/")
async def add_expense(expense: Expense):
    # Validate splits
    if expense.split_method == "percentage" and sum(expense.splits.values()) != 100:
        raise HTTPException(status_code=400, detail="Percentages must add up to 100")
    db.expenses.insert_one(expense.dict())
    return expense

@router.get("/expenses/{user_id}")
async def get_user_expenses(user_id: str):
    expenses = list(db.expenses.find({"user_id": user_id}))
    return expenses

@router.get("/expenses/")
async def get_all_expenses():
    expenses = list(db.expenses.find())
    return expenses
