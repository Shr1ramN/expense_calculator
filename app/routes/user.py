from fastapi import APIRouter, HTTPException
from typing import List
from app.models import User
from app.database import user_collection

router = APIRouter()

def user_helper(user) -> dict:
    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "mobile": user["mobile"],
    }

@router.post("/", response_description="Add new user", response_model=User)
async def create_user(user: User):
    user = user.dict()
    existing_user = await user_collection.find_one({"id": user["id"]})
    if existing_user:
        raise HTTPException(status_code=400, detail="User ID already exists")
    await user_collection.insert_one(user)
    created_user = await user_collection.find_one({"id": user["id"]})
    return user_helper(created_user)

@router.get("/{user_id}", response_description="Get a single user", response_model=User)
async def get_user(user_id: str):
    user = await user_collection.find_one({"id": user_id})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user_helper(user)
