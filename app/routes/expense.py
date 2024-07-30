from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from io import StringIO
import pandas as pd
from typing import List, Dict
from app.models import Expense
from app.database import expense_collection

router = APIRouter()

# Function to calculate user splits
def calculate_splits(expense: Expense) -> Dict[str, Dict[str, float]]:
    splits = {}
    if expense.split_method == 'equal':
        split_amount = expense.amount / len(expense.participants)
        for payer in expense.participants:
            splits[payer] = {}
            for participant in expense.participants:
                if payer != participant:
                    splits[payer][participant] = round(split_amount, 2)
    
    elif expense.split_method == 'exact':
        if expense.splits is None:
            raise HTTPException(status_code=400, detail="Exact splits must be provided")
        for payer in expense.participants:
            splits[payer] = {}
            if payer in expense.splits:
                for participant in expense.participants:
                    if payer != participant:
                        splits[payer][participant] = round(expense.splits[payer], 2)
    
    elif expense.split_method == 'percentage':
        if expense.splits is None:
            raise HTTPException(status_code=400, detail="Percentage splits must be provided")
        total_percentage = sum(expense.splits.values())
        if total_percentage != 100:
            raise HTTPException(status_code=400, detail="Percentages must add up to 100%")
        for payer in expense.participants:
            splits[payer] = {}
            if payer in expense.splits:
                for participant in expense.participants:
                    if payer != participant:
                        splits[payer][participant] = round((expense.splits[payer] / 100) * expense.amount, 2)
    
    return splits

# Helper function to format expenses
def expense_helper(expense) -> dict:
    return {
        "id": expense.get("id"),
        "payer": expense.get("payer"),
        "amount": expense.get("amount"),
        "participants": expense.get("participants"),
        "split_method": expense.get("split_method"),
        "splits": expense.get("splits"),
    }

# Function to calculate user balances
async def calculate_user_balances():
    expenses = await expense_collection.find().to_list(1000)
    user_balances = {}

    for expense in expenses:
        payer = expense.get("payer")
        amount = expense.get("amount")
        participants = expense.get("participants")
        splits = expense.get("splits", {})

        if expense.get("split_method") == "equal":
            split_amount = amount / len(participants)
            for participant in participants:
                if participant == payer:
                    continue
                if participant not in user_balances:
                    user_balances[participant] = {}
                if payer not in user_balances[participant]:
                    user_balances[participant][payer] = 0
                user_balances[participant][payer] -= split_amount
                if payer not in user_balances:
                    user_balances[payer] = {}
                if participant not in user_balances[payer]:
                    user_balances[payer][participant] = 0
                user_balances[payer][participant] += split_amount

        elif expense.get("split_method") == "exact":
            for participant, split_amount in splits.items():
                if participant == payer:
                    continue
                if participant not in user_balances:
                    user_balances[participant] = {}
                if payer not in user_balances[participant]:
                    user_balances[participant][payer] = 0
                user_balances[participant][payer] -= split_amount
                if payer not in user_balances:
                    user_balances[payer] = {}
                if participant not in user_balances[payer]:
                    user_balances[payer][participant] = 0
                user_balances[payer][participant] += split_amount

        elif expense.get("split_method") == "percentage":
            total_amount = amount
            for participant, percentage in splits.items():
                owed_amount = (percentage / 100) * total_amount
                if participant == payer:
                    continue
                if participant not in user_balances:
                    user_balances[participant] = {}
                if payer not in user_balances[participant]:
                    user_balances[participant][payer] = 0
                user_balances[participant][payer] -= owed_amount
                if payer not in user_balances:
                    user_balances[payer] = {}
                if participant not in user_balances[payer]:
                    user_balances[payer][participant] = 0
                user_balances[payer][participant] += owed_amount

    return user_balances

@router.post("/", response_description="Add new expense", response_model=Expense)
async def add_expense(expense: Expense):
    expense_dict = expense.dict()

    # Validate expense splits based on the split method
    if expense_dict['split_method'] == 'percentage':
        if expense_dict['splits'] is None or sum(expense_dict['splits'].values()) != 100:
            raise HTTPException(status_code=400, detail="Percentages must add up to 100%")
    
    # Calculate splits
    expense_dict['splits'] = calculate_splits(expense)

    # Check for existing expense
    existing_expense = await expense_collection.find_one({"id": expense_dict["id"]})
    if existing_expense:
        raise HTTPException(status_code=400, detail="Expense ID already exists")

    # Insert new expense
    result = await expense_collection.insert_one(expense_dict)
    created_expense = await expense_collection.find_one({"_id": result.inserted_id})

    return expense_helper(created_expense)

@router.get("/download", response_description="Download balance sheet")
async def download_balance_sheet():
    # Calculate user balances
    user_balances = await calculate_user_balances()
    
    # Convert to DataFrame
    rows = []
    for user, balances in user_balances.items():
        for other_user, amount in balances.items():
            rows.append({"User": user, "Owes To": other_user, "Amount": amount})
    
    df = pd.DataFrame(rows)
    
    # Create CSV file
    output = StringIO()
    df.to_csv(output, index=False)
    output.seek(0)

    # Return CSV file as response
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=balance_sheet.csv"}
    )

@router.get("/{user_id}", response_description="Get total amount to be paid by a user")
async def get_user_expenses(user_id: str):
    expenses = await expense_collection.find({"participants": user_id}).to_list(1000)
    
    total_amount = 0.0
    for expense in expenses:
        amount = expense.get("amount")
        payer = expense.get("payer")
        splits = expense.get("splits", {})

        if payer == user_id:
            total_amount -= amount
            for participant, amount_owed in splits.items():
                if participant == user_id:
                    total_amount += amount_owed
        else:
            total_amount += splits.get(user_id, 0)
    
    return {"user_id": user_id, "balance": total_amount}

@router.get("/", response_description="Get all expenses", response_model=List[Expense])
async def get_all_expenses():
    expenses = await expense_collection.find().to_list(1000)
    return [expense_helper(expense) for expense in expenses]