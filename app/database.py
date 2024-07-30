import motor.motor_asyncio
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_DETAILS = os.getenv("MONGO_URI")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client.expense_calculator

user_collection = database.get_collection("users")
expense_collection = database.get_collection("expenses")
