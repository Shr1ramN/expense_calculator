from fastapi import APIRouter, HTTPException
from typing import List, Dict
from app.models import Expense
from app.database import expense_collection

router = APIRouter()

def calculate_splits(expense: Expense) -> Dict[str, float]:
    splits = {}
    print(f"Calculating splits for expense: {expense}")
    if expense.split_method == 'equal':
        split_amount = expense.amount / len(expense.participants)
        print(f"Split amount per participant (equal): {split_amount}")
        for participant in expense.participants:
            splits[participant] = round(split_amount, 2)
    elif expense.split_method == 'exact':
        if expense.splits is None:
            raise HTTPException(status_code=400, detail="Exact splits must be provided")
        splits = expense.splits
    elif expense.split_method == 'percentage':
        if expense.splits is None:
            raise HTTPException(status_code=400, detail="Percentage splits must be provided")
        total_percentage = sum(expense.splits.values())
        if total_percentage != 100:
            raise HTTPException(status_code=400, detail="Percentages must add up to 100%")
        for participant, percentage in expense.splits.items():
            splits[participant] = round((percentage / 100) * expense.amount, 2)
    print(f"Calculated splits: {splits}")
    return splits

def expense_helper(expense) -> dict:
    return {
        "id": expense.get("id"),
        "payer": expense.get("payer"),
        "amount": expense.get("amount"),
        "participants": expense.get("participants"),
        "split_method": expense.get("split_method"),
        "splits": expense.get("splits"),
    }

@router.post("/", response_description="Add new expense", response_model=Expense)
async def add_expense(expense: Expense):
    expense_dict = expense.dict()
    print(f"Received expense payload: {expense_dict}")

    # Validate expense splits based on the split method
    if expense_dict['split_method'] == 'percentage':
        if expense_dict['splits'] is None or sum(expense_dict['splits'].values()) != 100:
            raise HTTPException(status_code=400, detail="Percentages must add up to 100%")
    
    # Calculate splits
    expense_dict['splits'] = calculate_splits(expense)
    print(f"Expense after calculating splits: {expense_dict}")

    # Check for existing expense
    existing_expense = await expense_collection.find_one({"id": expense_dict["id"]})
    if existing_expense:
        raise HTTPException(status_code=400, detail="Expense ID already exists")

    # Insert new expense
    result = await expense_collection.insert_one(expense_dict)
    created_expense = await expense_collection.find_one({"_id": result.inserted_id})

    print(f"Inserted expense: {created_expense}")
    return expense_helper(created_expense)

@router.get("/{user_id}", response_description="Get expenses for a user", response_model=List[Expense])
async def get_user_expenses(user_id: str):
    expenses = await expense_collection.find({"participants": user_id}).to_list(1000)
    return [expense_helper(expense) for expense in expenses]

@router.get("/", response_description="Get all expenses", response_model=List[Expense])
async def get_all_expenses():
    expenses = await expense_collection.find().to_list(1000)
    return [expense_helper(expense) for expense in expenses]

@router.get("/download", response_description="Download balance sheet")
async def download_balance_sheet():
    # Implement logic to generate and download balance sheet
    pass