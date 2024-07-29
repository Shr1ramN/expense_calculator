from fastapi import FastAPI
from app.routes import user, expense

app = FastAPI()

app.include_router(user.router, prefix="/api")
app.include_router(expense.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
