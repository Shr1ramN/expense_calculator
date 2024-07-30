from fastapi import FastAPI
from app.routes import user, expense

app = FastAPI()

app.include_router(user.router, prefix="/users", tags=["users"])
app.include_router(expense.router, prefix="/expenses", tags=["expenses"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Daily Expenses Sharing Application"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)